import pygame as py
import sys
import math

_ = False

RenderMap = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,_,_,_,_,1,1,1,1],
    [1,1,1,1,1,1,_,_,_,_,1,1,1,1],
    [1,_,_,_,_,_,_,_,_,_,_,_,1,1],
    [1,_,_,_,_,1,1,1,1,1,1,_,1,1],
    [1,_,_,_,_,1,1,1,1,1,1,_,1,1],
    [1,1,1,_,_,1,1,1,1,1,1,_,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

Resolution = Width,Height = 1402,702
HalfWidth = Width // 2
HalfHeight = Height // 2
FramesRendered = 0

PlayerPosition = 1.5,5
PlayerAngle = 0
PlayerSpeed = 0.004
PlayerRotationSpeed = 0.002

FieldOfView = math.pi / 3
Half_FieldOfView = FieldOfView / 2
NumberOfRaycasts = Width // 2
Half_NumberOfRaycasts = NumberOfRaycasts/2
Delta_Angle = FieldOfView / NumberOfRaycasts
MaximumDepth = 20

ScreenDistance = HalfWidth / math.tan(Half_FieldOfView)
Scale = Width // NumberOfRaycasts

TextureSize = 256
HalfTextureSize = TextureSize // 2


class ObjectRender:
    def __init__(self,game):
        self.game = game
        self.screen = game.screen
        self.WallTextures = self.LoadTexture()

    @staticmethod
    def FetchTexture(path, res=(TextureSize, TextureSize)):
        Texture = py.image.load(path).convert_alpha()
        return py.transform.scale(Texture, res)

    def LoadTexture(self):
        return {
            1: self.FetchTexture('Textures/Wall.jpg'),
            2: self.FetchTexture('Textures/Floor.jpg'),
            3: self.FetchTexture('Textures/Planks Texture.jpg'),
        }
    

class Raycasting:
    def __init__(self,game):
        self.game = game

    def Ray_Cast(self):
        ox, oy = self.game.player.Position
        x_map, y_map= self.game.player.Map_Position
        
        ray_angle = self.game.player.angle - Half_FieldOfView + 0.0001
        for ray in range(NumberOfRaycasts):
            SinA = math.sin(ray_angle)
            CosA = math.cos(ray_angle)

            Y_Horizontal,dy = (y_map + 1, 1) if SinA >0 else (y_map - 1e-6, -1)
            DepthHorizontal = (Y_Horizontal - oy) / SinA
            X_Horizontal = ox + DepthHorizontal * CosA

            DeltaDepth = dy / SinA
            dx = DeltaDepth * CosA

            for i in range(MaximumDepth):
                tile_horizontal = int(X_Horizontal), int(Y_Horizontal)
                if tile_horizontal in self.game.map.WorldMap:
                    break
                X_Horizontal += dx
                Y_Horizontal += dy
                DepthHorizontal += DeltaDepth

            X_Verticle, dx = (x_map + 1,1) if CosA > 0 else (x_map - 1e-6, -1)
            DepthVerticle = (X_Verticle - ox) / CosA
            Y_Verticle = oy + DepthVerticle * SinA

            DeltaDepth  = dx / CosA
            dy = DeltaDepth * SinA

            for i in range(MaximumDepth):
                tile_verticle = int (X_Verticle), int(Y_Verticle)
                if tile_verticle in self.game.map.WorldMap:
                    break
                X_Verticle += dx
                Y_Verticle += dy
                DepthVerticle += DeltaDepth

            if DepthVerticle < DepthHorizontal:
                Depth = DepthVerticle
            else:
                Depth = DepthHorizontal

            Depth *= math.cos(self.game.player.angle - ray_angle)
            
            ProjectionHeight = ScreenDistance / (Depth + 0.0001)

            Colour = [255 / (1 + Depth ** 5 * 0.00002)] * 3
            py.draw.rect(self.game.screen, Colour,
                         (ray * Scale, HalfHeight - ProjectionHeight // 2, Scale, ProjectionHeight))
            
            ray_angle += Delta_Angle

    def Update(self):
        self.Ray_Cast()

class Player:
    def __init__(self,game):
        self.game = game
        self.x, self.y = PlayerPosition
        self.angle = PlayerAngle

    def Movement(self):
        SinA = math.sin(self.angle)
        CosA = math.cos(self.angle)
        dx, dy = 0, 0
        Speed = PlayerSpeed * self.game.DeltaTime
        SpeedSin = Speed * SinA
        SpeedCos = Speed * CosA

        Keys = py.key.get_pressed()
        if Keys[py.K_w]:
            dx += SpeedCos
            dy += SpeedSin
        if Keys[py.K_s]:
            dx += -SpeedCos
            dy += -SpeedSin
        if Keys[py.K_a]:
            dx += SpeedSin
            dy += -SpeedCos
        if Keys[py.K_d]:
            dx += -SpeedSin
            dy += SpeedCos

        self.CheckCollision(dx,dy)
        
        if Keys[py.K_LEFT]:
            self.angle -= PlayerRotationSpeed * self.game.DeltaTime
        if Keys[py.K_RIGHT]:
            self.angle += PlayerRotationSpeed * self.game.DeltaTime
        self.angle %= math.tau

    def CheckHit(self,x,y):
        return (x, y) not in self.game.map.WorldMap

    def CheckCollision(self,dx,dy):
        if self.CheckHit(int(self.x + dx), int(self.y)):
            self.x += dx
        if self.CheckHit(int(self.x), int(self.y + dy)):
            self.y += dy
    
    def Draw(self):
        #py.draw.line(self.game.screen, 'yellow', (self.x* 100, self.y * 100),
                           #(self.x * 100 + Width * math.cos(self.angle),
                             #self.y * 100 + Width * math.sin(self.angle)),2)
        py.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)
            

    def Update(self):
        self.Movement()

    @property
    def Position(self):
        return self.x, self.y

    @property
    def Map_Position(self):
        return int(self.x), int(self.y)

class Map:
    def __init__(self,game):
        self.game = game
        self.GameMap = RenderMap
        self.WorldMap = {}
        self.FetchMap()

    def FetchMap(self):
        for j,row in enumerate(self.GameMap):
            for i,value in enumerate(row):
                if value:
                    self.WorldMap[(i, j)] = value

    def Draw(self):
        [py.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
         for pos in self.WorldMap]

class MurderMystery:
    def __init__(self):
        py.init()
        self.screen = py.display.set_mode(Resolution)
        self.clock = py.time.Clock()
        self.DeltaTime = 1
        self.NewGame()

    def NewGame(self):
        self.map = Map(self)
        self.player = Player(self)
        self.ObjectRender = ObjectRender(self)
        self.raycasting = Raycasting(self)

    def Update(self):
        self.player.Update()
        self.raycasting.Update()
        py.display.flip()
        self.DeltaTime = self.clock.tick(FramesRendered)
        py.display.set_caption(f'{self.clock.get_fps() : .1f}')

    def Draw(self):
        self.screen.fill('black')
        #self.map.Draw()
        #self.player.Draw()

    def Events(self):
        for event in py.event.get():
            if event.type == py.QUIT or (event.type == py.KEYDOWN and event.key == py.K_ESCAPE):
                py.quit()
                sys.exit()
    
    def Run(self):
        while True:
            self.Events()
            self.Update()
            self.Draw()

if __name__ == '__main__' :
    game = MurderMystery()
    game.Run()
        
