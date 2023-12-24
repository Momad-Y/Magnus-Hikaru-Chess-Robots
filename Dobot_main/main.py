# Created by Hugo Nolte for course PA1414 - DoBot Magician Project
# 2019

import threading
import DoBotArm as Dbt

#Example of bundling functions
def functons():
    homeX, homeY, homeZ = 250, 0, 50
    dobot = Dbt.DoBotArm(homeX, homeY, homeZ) #Create DoBot Class Object with home position x,y,z
    dobot.moveArmXY(250, 100)
    dobot.pickToggle(-40)
    dobot.toggleSuction()
    dobot.pickToggle(-40)
    dobot.moveHome()
    dobot.pickToggle(-40)
    dobot.toggleSuction()
    dobot.pickToggle(-40)

def manualMode():
    homeX, homeY, homeZ = 250, 0, 50
    dobot = Dbt.DoBotArm(homeX, homeY, homeZ) #Create DoBot Class Object with home position x,y,z
    print("1- Go Home (250, 0, 50)")
    print("2- Move X,Y")
    print("3- pick")
    print("4- Grip")
    print("5- toggles suction")
    print("6- get Position")
    print("0 - exit")
    while True:
        option = int(input(">> "))
        if(option == 1): dobot.moveHome()
        elif(option == 2):
            x = int(input("X: "))
            y = int(input("Y: "))
            dobot.moveArmXY(x,y)
        elif(option == 3):
            height = int(input("height: "))
            dobot.pickToggle(height)
        elif(option == 4): dobot.toggleGrip()
        elif(option == 5): dobot.toggleSuction()
        elif(option == 6):
            pos = dobot.getPos()
            print("POS: ({}, {}, {})".format(pos[0], pos[1], pos[2]))
        elif(option == 0): break
        else: print("Unrecognized command")

def autoMode():
    homeX, homeY, homeZ = 250, 0, 50
    dobot = Dbt.DoBotArm(homeX, homeY, homeZ)
    dobot.goPick((250, 50, -30), (150, 100, -30))
    # dobot.setGrip(False)
    # dobot.pick(-35)
    # dobot.setGrip(True)
    # dobot.moveArmXY(150, 100)
    # dobot.pick(-30)
    # dobot.setGrip(False)
    # dobot.pick(0)
#--Main Program--
def main():
    # manualMode()
    autoMode()

main()
