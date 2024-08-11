"""
Copyright (C) 2022-2023 Excilious

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pygame as py
import time
from random import randint
import sys
import math

_ = False

RenderMap = {
    "Default":
    [
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],
            [_,_,_,_,_,_,_,_,_,_,_,_,_,_],

    ],
}


Resolution = Width,Height = 1402,702
HalfWidth = Width // 2
HalfHeight = Height // 2
FramesRendered = 60

PlayerPosition = 1.5,5
PlayerAngle = 0
PlayerSpeed = 0.004
PlayerRotationSpeed = 0.002
PlayerSizeScale = 60

MouseSensitivity = 0.0003
MouseMaxRel = 40
MouseBorderLeft = 100
MouseBorderRight = Width - MouseBorderLeft

Countdown = 30
Players = {}
MaxPlayers = 11

FieldOfView = math.pi / 3
Half_FieldOfView = FieldOfView / 2
NumberOfRaycasts = Width // 2
Half_NumberOfRaycasts = NumberOfRaycasts/2
Delta_Angle = FieldOfView / NumberOfRaycasts
MaximumDepth = 20

LocalPlayerName = []
ScreenDistance = HalfWidth / math.tan(Half_FieldOfView)
Scale = Width // NumberOfRaycasts

TextureSize = 256
HalfTextureSize = TextureSize // 2

class MurderGame:
    def __init__(self,game):
        self.game = game
        self.PropertiesCreated = False

    def Intermission(self):
        while Countdown > 0:
            Countdown -= 1

    def Update(self):
        if self.PropertiesCreated == True:
            CodeTextures = py.image.load(self.CodeImage).convert_alpha()
            RoleTextures = py.image.load(self.RoleImage).convert_alpha()
            self.RenderedCode = py.transform.scale(CodeTextures,(190,55))
            self.RenderedRole = py.transform.scale(RoleTextures,(200,60))
            self.game.screen.blit(self.RenderedCode,(-10,630))
            self.game.screen.blit(self.RenderedRole,(590,0))

class ObjectRenderer:
    def  __init__(self,game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.LoadWallTextures()
        self.players = Player(self)
        self.skyoffset = 0
        self.skyimage = self.Get_Texture('Textures/Sky.jpg',(Width, HalfHeight))
        self.Textures  = {
            1: self.Get_Texture('Textures/Wall.png'),
            2: self.Get_Texture('Textures/Planks Texture.jpg'),
            3: self.Get_Texture('Textures/Wall.png'),
            4: self.Get_Texture('Textures/Wall.png'),
            5: self.Get_Texture('Textures/Wall.png'),
        }

    def Draw(self):
        self.DrawBackground()
        self.RenderGameObjects()

    def DrawBackground(self):
        py.draw.rect(self.screen, (255,0,0),(0, HalfHeight, Width, Height))


    def RenderGameObjects(self):
        ListObjects = self.game.raycasting.ObjectsQueueRender
        for Depth,Image,Position in ListObjects:
            self.screen.blit(Image, Position)

    @staticmethod
    def Get_Texture(path, res=(TextureSize, TextureSize)):
        Textures = py.image.load(path).convert_alpha()
        return py.transform.scale(Textures, res)

    def LoadWallTextures(self):
        return {
            1: self.Get_Texture('Textures/Wall.png'),
            2: self.Get_Texture('Textures/Wall.png'),
            3: self.Get_Texture('Textures/Wall.png'),
            4: self.Get_Texture('Textures/Wall.png'),
            5: self.Get_Texture('Textures/Wall.png'),
        }
    


class Raycasting:
    def __init__(self,game):
        self.game = game
        self.RaycastResults = []
        self.ObjectsQueueRender = []   
        self.Textures = self.game.objectrenderer.LoadWallTextures
        TextureVerticle,TextureHorizontal = 1,1

    def GetObjectsToRender(self):
        self.ObjectsQueueRender = []
        for Ray,Values in enumerate(self.RaycastResults):
            Depth, ProjectionHeight, Texture, Offset  = Values
            if ProjectionHeight < Height:
                Wall_Column = self.game.objectrenderer.Textures[Texture].subsurface(
                    Offset * (TextureSize - Scale), 0, Scale, TextureSize
                )
                Wall_Column = py.transform.scale(Wall_Column, (Scale, int(ProjectionHeight)))
                Wall_Position = (Ray * Scale, HalfHeight - ProjectionHeight // 2)
            else:
                Texture_Height = TextureSize * Height / ProjectionHeight
                Wall_Column = self.game.objectrenderer.Textures[Texture].subsurface(
                    Offset * (TextureSize - Scale), HalfTextureSize - Texture_Height // 2,
                    Scale, Texture_Height
                )
                Wall_Column = py.transform.scale(Wall_Column, (Scale,Height))
                Wall_Position = (Ray * Scale,0)

            self.ObjectsQueueRender.append((Depth, Wall_Column, Wall_Position))

    def Ray_Cast(self):
        self.RaycastResults = []
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
                    TextureHorizontal = self.game.map.WorldMap[tile_horizontal]
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
                    TextureVerticle = self.game.map.WorldMap[tile_verticle]
                    break
                X_Verticle += dx
                Y_Verticle += dy
                DepthVerticle += DeltaDepth

            if DepthVerticle < DepthHorizontal:
                Depth, Texture = DepthVerticle, TextureVerticle
                Y_Verticle %= 1
                Offset = Y_Verticle if CosA > 0 else (1 - Y_Verticle)
            else:
                Depth, Texture = DepthHorizontal, TextureHorizontal
                X_Horizontal %= 1
                Offset = (1 - X_Horizontal) if SinA > 0 else X_Horizontal
            Depth *= math.cos(self.game.player.angle - ray_angle)
            
            ProjectionHeight = ScreenDistance / (Depth + 0.0001)

            self.RaycastResults.append((Depth, ProjectionHeight, Texture, Offset))
            
            ray_angle += Delta_Angle

    def Update(self):
        self.Ray_Cast()
        self.GetObjectsToRender()

class Player:
    def __init__(self,game):
        self.game = game
        self.rel = py.mouse.get_rel()[0]
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

    def MouseControl(self):
        MouseClicked = py.mouse.get_pressed()
        if MouseClicked[2]:
            if py.mouse.get_pressed()[0]:
                MouseX, MouseY = py.mouse.get_pos()
                if MouseX < MouseBorderLeft or MouseX > MouseBorderRight:
                    py.mouse.set_pos([HalfWidth, HalfHeight])
                    
            self.rel = py.mouse.get_rel()[0]
            self.rel = max(-MouseMaxRel, min(MouseMaxRel, self.rel))
            self.angle += self.rel * MouseSensitivity * self.game.DeltaTime
    
    def CheckHit(self,x,y):
        return (x, y) not in self.game.map.WorldMap

    def CheckCollision(self,dx,dy):
        Scale = PlayerSizeScale / self.game.DeltaTime
        if self.CheckHit(int(self.x + dx * Scale), int(self.y)):
            self.x += dx
        if self.CheckHit(int(self.x), int(self.y + dy * Scale)):
            self.y += dy
    
    def Draw(self):
        #py.draw.line(self.game.screen, 'yellow', (self.x* 100, self.y * 100),
                           #(self.x * 100 + Width * math.cos(self.angle),
                             #self.y * 100 + Width * math.sin(self.angle)),2)
        py.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)
            

    def Update(self):
        self.MouseControl()
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
        self.GameMap = RenderMap["Default"]
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
        self.objectrenderer = ObjectRenderer(self)
        self.raycasting = Raycasting(self)
        self.maingame = MurderGame(self)

    def Update(self):
        self.player.Update()
        self.raycasting.Update()
        self.maingame.Update()
        py.display.flip()
        self.DeltaTime = self.clock.tick(FramesRendered)
        py.display.set_caption(f'{self.clock.get_fps() : .1f}')

    def Draw(self):
        self.screen.fill((230,230,230))
        self.objectrenderer.Draw()
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
        
