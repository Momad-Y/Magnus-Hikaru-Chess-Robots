import C2M as c2m
import DrDRA as dr

cam_id = 0
cam = c2m.init_cam(cam_id)
square_size_offset = -8
column_offset = -2
row_offset = -1

home_cartesian = (75, 170, 0)

dobot = dr.init_arm("../Playback Files/Final Coordinates.xml")

dr.go_to_home(dobot)
dr.go_to_home(dobot)

filler_img = c2m.grab_img(cam)
empty_img = c2m.grab_img(cam)

c2m.show_img(empty_img, "Empty", image_resolution=empty_img.shape)  # type: ignore

corners = c2m.find_chessboard_corners(empty_img, square_size_offset)  # type: ignore

cam_coordinates = c2m.find_squares_coordinates(
    corners, square_size_offset, column_offset, row_offset  # type: ignore
)

dobot_coordinates = c2m.cam_2_arm_transformation(cam_coordinates)

print("Cam Coordinates:")
print(cam_coordinates)

with open("../Test/cam_coordinates.txt", "w") as f:
    # loop across the keys and values in the dictionary
    for key, value in cam_coordinates.items():
        f.write(str(key) + ": " + str(value) + " cm\n")

print()

print("Dobot Coordinates:")
print(dobot_coordinates)

with open("../Test/dobot_coordinates.txt", "w") as f:
    for key, value in dobot_coordinates.items():
        f.write(str(key) + ": " + str(value) + " cm\n")


homography = c2m.get_homography_matrix(empty_img, "../Images/Motherboard.jpg")  # type: ignore

empty_img, flip = c2m.warp_img(empty_img, homography)  # type: ignore

empty_img = c2m.flip_img(empty_img, flip)

c2m.show_img(empty_img, "Empty Cropped", image_resolution=empty_img.shape)

dr.go_to_home(dobot)

# input("Press Enter to continue...")

# filler_img = c2m.grab_img(cam)
# prev_img = c2m.grab_img(cam)

# prev_img, flip = c2m.warp_img(prev_img, homography)

# prev_img = c2m.flip_img(prev_img, flip)

# c2m.show_img(prev_img, "Previous Cropped", image_resolution=prev_img.shape)

# input("Press Enter to continue...")

# filler_img = c2m.grab_img(cam)
# curr_img = c2m.grab_img(cam)

# curr_img, flip = c2m.warp_img(curr_img, homography)

# curr_img = c2m.flip_img(curr_img, flip)

# c2m.show_img(curr_img, "Current Cropped", image_resolution=curr_img.shape)

# moves, confidence = c2m.find_moves(prev_img, curr_img)

moves = ["f5", "e4", "f5e4"]

print(moves)
print()

# db.apply_move(dobot, moves[2], False, False, False)
