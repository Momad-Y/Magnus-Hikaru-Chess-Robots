import C2M as c2m
import cv2

cam_id = 0
cam = c2m.init_cam(cam_id)
square_size_offset = -8
column_offset = -2
row_offset = -1

filler_img = c2m.grab_img(cam)
empty_img = c2m.grab_img(cam)
# empty_img = c2m.read_img("./Test/Live Empty.jpg")  # Test

c2m.show_img(empty_img, "Empty", image_resolution=empty_img.shape)  # type: ignore

corners = c2m.find_chessboard_corners(empty_img, square_size_offset)  # type: ignore

coordinates = c2m.find_squares_coordinates(
    corners, square_size_offset, column_offset, row_offset  # type: ignore
)  # Should be done before homography

homography = c2m.get_homography_matrix(empty_img, "Images/Motherboard.jpg")  # type: ignore

empty_img, flip = c2m.warp_img(empty_img, homography)  # type: ignore

empty_img = c2m.flip_img(empty_img, flip)

c2m.show_img(empty_img, "Empty Cropped", image_resolution=empty_img.shape)

input("Press Enter to continue...")

filler_img = c2m.grab_img(cam)
prev_img = c2m.grab_img(cam)
# prev_img = c2m.read_img("./Test/Dataset Previous.jpg")  # Test

prev_img, flip = c2m.warp_img(prev_img, homography)  # type: ignore

prev_img = c2m.flip_img(prev_img, flip)

c2m.show_img(prev_img, "Previous Cropped", image_resolution=prev_img.shape)

input("Press Enter to continue...")

filler_img = c2m.grab_img(cam)
curr_img = c2m.grab_img(cam)
# curr_img = c2m.read_img("./Test/Dataset Current.jpg")  # Test

curr_img, flip = c2m.warp_img(curr_img, homography)  # type: ignore

curr_img = c2m.flip_img(curr_img, flip)

c2m.show_img(curr_img, "Current Cropped", image_resolution=curr_img.shape)

moves, confidence = c2m.find_moves(prev_img, curr_img)

print("Moves:")
print(moves)
print()
print("Confidence:")
print(confidence)
print()
print("Coordinates:")
print(coordinates)

# Get the coordinates of the squares that have moved
moved_coordinates = []
for move in moves:  # type: ignore
    moved_coordinates.append(coordinates[move])

print()
print("Moved Coordinates:")
print(moved_coordinates)
