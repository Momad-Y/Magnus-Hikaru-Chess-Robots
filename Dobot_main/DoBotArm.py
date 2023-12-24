# /usr/bin/env python
import Dobot_main.DobotDllType as dType
import sys, os
import time

os.chdir(os.getcwd() + "\Dobot_main")  # type: ignore
sys.path.insert(1, "./DLL")

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",  # type: ignore
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",  # type: ignore
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied",  # type: ignore
}


# Main control class for the DoBot Magician.
class DoBotArm:
    def __init__(self, homeX, homeY, homeZ):
        self.suction = False
        self.picking = False
        self.griping = False
        self.api = dType.load()
        self.homeX = homeX
        self.homeY = homeY
        self.homeZ = homeZ
        self.connected = False
        self.dobotConnect()

    def __del__(self):
        self.dobotDisconnect()

    # Attempts to connect to the dobot
    def dobotConnect(self):
        if self.connected:
            print("You're already connected")
        else:
            state = dType.ConnectDobot(self.api, "", 115200)[0]
            if state == dType.DobotConnect.DobotConnect_NoError:  # type: ignore
                print("Connect status:", CON_STR[state])
                dType.SetQueuedCmdClear(self.api)
                self.connected = True
                return self.connected
            else:
                print("Unable to connect")
                print("Connect status:", CON_STR[state])
                return self.connected

    def dobotConnect2(self):
        if self.connected:
            print("You're already connected")
        else:
            state = dType.ConnectDobot(self.api, "", 115200)[0]
            if state == dType.DobotConnect.DobotConnect_NoError:  # type: ignore
                print("Connect status:", CON_STR[state])
                dType.SetQueuedCmdClear(self.api)

                dType.SetHOMEParams(
                    self.api, self.homeX, self.homeY, self.homeZ, 0, isQueued=1
                )
                dType.SetPTPJointParams(
                    self.api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1
                )
                dType.SetPTPCommonParams(self.api, 100, 100, isQueued=1)

                dType.SetHOMECmd(self.api, temp=0, isQueued=1)
                self.connected = True
                return self.connected
            else:
                print("Unable to connect")
                print("Connect status:", CON_STR[state])
                return self.connected

    # Returns to home location and then disconnects
    def dobotDisconnect(self):
        self.moveHome()
        dType.DisconnectDobot(self.api)

    # Delays commands
    def waitCommand(self, cmdIndex):
        dType.SetQueuedCmdStartExec(self.api)
        while cmdIndex > dType.GetQueuedCmdCurrentIndex(self.api)[0]:
            dType.time.sleep(2)
        dType.SetQueuedCmdStopExec(self.api)

    # Moves arm to X/Y/Z Location
    def moveArmXY(self, x, y):
        lastIndex = dType.SetPTPCmd(
            self.api, dType.PTPMode.PTPMOVLXYZMode, x, y, self.homeZ, 1  # type: ignore
        )[0]
        self.waitCommand(lastIndex)

    # Returns to home location
    def moveHome(self):
        lastIndex = dType.SetPTPCmd(
            self.api,
            dType.PTPMode.PTPMOVLXYZMode,  # type: ignore
            self.homeX,
            self.homeY,
            self.homeZ,
            0,
        )[0]
        self.waitCommand(lastIndex)

    # ============================================================================
    def goPick(self, source, dest):
        self.setGrip(False)
        self.moveArmXY(source[0], source[1])
        self.pick(source[2])
        self.setGrip(True)
        self.pick(0)
        self.moveArmXY(dest[0], dest[1])
        self.pick(dest[2])
        self.setGrip(False)
        self.pick(0)

    # ============================================================================
    def pick(self, itemHeight):
        positions = dType.GetPose(self.api)
        cmdIndex = dType.SetPTPCmd(
            self.api,
            dType.PTPMode.PTPMOVLXYZMode,  # type: ignore
            positions[0],
            positions[1],
            itemHeight,
            1,
        )[0]
        self.waitCommand(cmdIndex)

    # ============================================================================
    def toggleGrip(self):
        self.griping = not self.griping
        self.setGrip(self.griping)

    # ============================================================================
    def setGrip(self, state=False):
        self.griping = state
        cmdIndex = dType.SetEndEffectorGripper(self.api, True, state, isQueued=0)[0]
        self.waitCommand(cmdIndex)
        dType.time.sleep(200)
        self.setSuction(False)

    # ============================================================================
    def toggleSuction(self):
        self.suction = not self.suction
        self.setSuction(self.suction)

    # ============================================================================
    def setSuction(self, state=False):
        self.suction = state
        cmdIndex = dType.SetEndEffectorSuctionCup(self.api, True, state, isQueued=0)[0]
        self.waitCommand(cmdIndex)

    # ============================================================================
    def getPos(self):
        return dType.GetPose(self.api)

    # ============================================================================
    def move_arm_xy_linear(self, x, y):
        lastIndex = dType.SetPTPCmd(
            self.api, dType.PTPMode.PTPMOVLXYZMode, x, y, self.homeZ, 0  # type: ignore
        )[0]
        self.waitCommand(lastIndex)

    # ============================================================================
    def move_arm_XY_ptp(self, x, y):
        lastIndex = dType.SetPTPCmd(
            self.api, dType.PTPMode.PTPMOVJXYZMode, x, y, self.homeZ, 0  # type: ignore
        )[0]
        self.waitCommand(lastIndex)
