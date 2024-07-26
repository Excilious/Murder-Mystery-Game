v1 = True
count = 1
Contents = ""

def SaveContents(Contents):
    File = open("Contents.txt","w")
    File.write(Contents)
    File.close()

while v1:
    Choice = input("[>]")
    if Choice == "`":
        v1 = False
    else:
        Contents += str(count)+") "+str(Choice)+"\n"
        print("Ready to print:")
        count += 1
        print(Contents)
        SaveContents(Contents)
        
