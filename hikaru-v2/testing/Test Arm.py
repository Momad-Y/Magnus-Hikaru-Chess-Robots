import DrDRA as dr
import os

cwd = os.getcwd()

arm = dr.init_arm(cwd + "/../Calibration Files/Calibration.xml")

dr.go_to_calibration(arm)

dr.go_to_home(arm)

dr.go_to_cell_str(arm, "d5")

dr.go_to_cell_str(arm, "d8")

dr.go_to_home(arm)
