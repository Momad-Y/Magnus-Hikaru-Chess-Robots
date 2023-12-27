import cv2
import string
import numpy as np
from math import pi
from PIL import Image, ImageTk

board_pattern_size = (
    7,
    7,
)  # Number of squares in a row/column of the chessboard to be detected
raw_img_resolution = ()  # Initialize the raw_img_resolution variable to store the resolution of the raw images
img_resolution = (400, 400)  # Resolution of the images to be used
num_of_squares = 8  # Number of squares in a row/column of the chessboard
pixel_2_cm_ratio = 0  # Initialize the cm_to_pixel variable to store the conversion factor from cm to pixel
camera_width_fov = 42  # Width field of view of the camera in degrees


def init_cam(cam_identification: int or str):
    """
    Initializes the camera.

    Args:
    -   cam_identification (int or str): The camera identification number or the IP address of the camera.

    Returns:
    -   cv2.VideoCapture: The camera object.
    """

    # If the camera identification is a string, it is the IP address of the camera
    if isinstance(cam_identification, str):
        return cv2.VideoCapture("http://" + cam_identification + "/video")

    return cv2.VideoCapture(
        cam_identification, cv2.CAP_DSHOW
    )  # Else, it is the camera identification number


def show_img(img: np.ndarray, window_name: str, image_resolution: tuple):
    """
    Display an image in a named window.

    Args:
    -   img (numpy.ndarray): The image to be displayed.
    -   window_name (str): The name of the window.

    Returns:
    -   None
    """

    cv2.namedWindow(window_name)  # Create a named window
    cv2.resizeWindow(
        window_name, image_resolution[0], image_resolution[1]
    )  # Resize the window to the image resolution
    cv2.imshow(window_name, img)  # Display the image
    cv2.waitKey(0)  # Wait for a key press


def grab_img(cam: cv2.VideoCapture):
    """
    Takes a picture using the camera, then returns it as a numpy array.

    Args:
    -   cam (cv2.VideoCapture): The camera object.

    Returns:
    -   img (numpy.ndarray): The image as a numpy array, or None if the image could not be taken.
    """

    global raw_img_resolution  # Make the raw_img_resolution variable global
    global pixel_2_cm_ratio  # Make the cm_to_pixel variable global

    # Take picture
    result, img = cam.read()

    # If the picture could not be taken, raise an exception
    if not result:
        return None

    raw_img_resolution = img.shape

    pixel_2_cm_ratio = (
        camera_width_fov / raw_img_resolution[1]
    )  # Conversion factor from cm to pixel (camera_width_fov cm across the width of the field of view of the camera)

    return img  # Return the image


def read_img(path: str):
    """
    Reads an image from a file and returns it as a numpy array.

    Args:
    -   path (str): The path to the image file.

    Returns:
    -   img: The image as a numpy array, or None if the image could not be read.
    """

    global raw_img_resolution  # Make the raw_img_resolution variable global
    global pixel_2_cm_ratio  # Make the cm_to_pixel variable global

    img = cv2.imread(path)

    if img is None:
        return None

    raw_img_resolution = img.shape

    pixel_2_cm_ratio = (
        camera_width_fov / raw_img_resolution[1]
    )  # Conversion factor from cm to pixel (camera_width_fov cm across the width of the field of view of the camera)

    return img


def get_homography_matrix(img: np.ndarray, motherboard_path: str):
    """
    Finds the homography matrix between the current image of the board and the reference board image

    Args :
    -   img (ndarray) : The current image of the full chess board in BGR color format
    -   motherboard_path (str) : The path to the reference board image

    Returns :
    -   homography_matrix (ndarray) : Homography matrix between the two images or None if the corners were not found in either image
    """

    motherboard = read_img(motherboard_path)  # Get the reference board image

    lower_HSV = np.array([0, 0, 143])  # Lower HSV values for the image masks
    upper_HSV = np.array([179, 61, 252])  # Upper HSV values for the image masks

    HSV_img = cv2.cvtColor(
        img, cv2.COLOR_BGR2HSV
    )  # Convert the board's image to HSV format
    img_mask = cv2.inRange(
        HSV_img, lower_HSV, upper_HSV
    )  # Create a mask for the board's image using the HSV values

    HSV_motherboard = cv2.cvtColor(
        motherboard, cv2.COLOR_BGR2HSV  # type: ignore
    )  # Convert the reference board image to HSV format
    motherboard_mask = cv2.inRange(
        HSV_motherboard, lower_HSV, upper_HSV
    )  # Create a mask for the reference board image using the HSV values

    img_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (50, 30)
    )  # Kernel for the board's image mask

    dilated_img_kernel = cv2.dilate(
        img_mask, img_kernel, iterations=5
    )  # Dilate the board's mask to get the full board

    result_img = 255 - cv2.bitwise_and(
        dilated_img_kernel, img_mask
    )  # type: ignore # Get the board's image mask without the background

    motherboard_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (50, 30)
    )  # Kernel for the mask of the reference board image

    dilated_motherboard_kernel = cv2.dilate(
        motherboard_mask, motherboard_kernel, iterations=5
    )  # Dilate the mask of the reference board image to get the full board

    result_motherboard = 255 - cv2.bitwise_and(
        dilated_motherboard_kernel, motherboard_mask
    )  # type: ignore # Get the mask of the reference board image without the background

    # Convert the images to uint8 format
    result_img = np.uint8(result_img)
    result_motherboard = np.uint8(result_motherboard)

    # show_img(result_img, "result_img", result_img.shape)  # type: ignore # Test

    return_img, img_corners = cv2.findChessboardCorners(
        result_img,  # type: ignore
        board_pattern_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )  # type: ignore # Find the corners of the chessboard in the image

    # show_img(result_img, "result_img", result_img.shape) # type: ignore # Test

    return_motherboard, motherboard_corners = cv2.findChessboardCorners(  # type: ignore
        result_motherboard,  # type: ignore
        board_pattern_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )  # Find the corners of the chessboard in the reference board image

    # Check if the corners were found in both images
    if return_img and return_motherboard:
        homography_matrix, _ = cv2.findHomography(
            img_corners, motherboard_corners, cv2.RANSAC, 5.0
        )  # Find the homography matrix between the two images using the corners

        return homography_matrix  # Return the homography matrix
    else:
        return None  # Return None if the corners were not found in either image


def modify_homography_matrix(homography_matrix: np.ndarray):
    """
    Modifies the homography matrix to make fix the rotation of the warped image.

    Args:
    -   homography_matrix (np.ndarray): The original homography matrix.

    Returns:
    -   np.ndarray: The modified homography matrix.
    """

    # Initialize the modified homography matrix with zeros
    modified_homography_matrix = np.zeros((3, 3))

    # Iterate through the homography matrix
    for i in range(3):
        for j in range(3):
            if (
                abs(int(homography_matrix[i][j])) == 1
            ):  # Check if the integer part of the element is 1 or -1
                # Add the row to the modified homography matrix
                modified_homography_matrix[j] += homography_matrix[i]

    # Check if the final row of the modified homography matrix is [0, 0, 0]
    if np.array_equal(modified_homography_matrix[2], np.array([0, 0, 0])):
        # Replace the final row with final row of the original homography matrix
        modified_homography_matrix[2] = homography_matrix[2]

    return modified_homography_matrix  # Return the modified homography matrix


def warp_img(img: np.ndarray, homography_matrix: np.ndarray):
    """
    Warps an image using a given homography matrix.

    Args:
        img (np.ndarray): The input image to be warped.
        homography_matrix (np.ndarray): The homography matrix used for warping.

    Returns:
        tuple: A tuple containing the warped image and a boolean indicating whether the image was flipped.
    """

    flip = False  # Initialize the flip variable to False which indicates whether the image needs to be flipped or not

    # Modify the homography matrix to fix the rotation of the warped image
    homography_matrix = modify_homography_matrix(homography_matrix)

    # Check if the first element of the homography matrix is -1
    if int(homography_matrix[0][0]) == -1:
        # Multiply the homography matrix by -1
        homography_matrix = np.multiply(homography_matrix, -1)
        flip = True  # Set the flip variable to True

    warped_img = cv2.warpPerspective(img, homography_matrix, img_resolution)

    return (warped_img, flip)  # Return the warped image and the flip variable


def find_moves(prev_img: np.ndarray, cur_img: np.ndarray):
    """
    Finds the moves made on a chessboard based on the difference between two images.

    Args:
    -   prev_img (np.ndarray): The previous image of the chessboard.
    -   cur_img (np.ndarray): The current image of the chessboard.

    Returns:
    -   tuple: A tuple containing the moves list and the confidence rate list, or None if no moves were found.
    """

    max_num_of_moves = 4  # Maximum number of moves to be returned
    square_size = int(
        img_resolution[0] / num_of_squares
    )  # Size of each square in the chessboard

    confidence_rate_list = [
        0 for _ in range(max_num_of_moves)
    ]  # Initialize the confidence rate list with zeros

    moves_list = [
        "0" for _ in range(max_num_of_moves)
    ]  # Initialize the moves list with zeros

    # Iterate through the chessboard squares
    for i in range(
        0, num_of_squares * square_size, square_size
    ):  # Iterate through rows
        k = 0  # Initializing a counter for each row
        for j in range(
            0, num_of_squares * square_size, square_size
        ):  # Iterate through columns
            prev_img_square = prev_img[
                i : i + square_size, j : j + square_size
            ]  # Get the square from the previous image
            cur_img_square = cur_img[
                i : i + square_size, j : j + square_size
            ]  # Get the square from the current image

            # Calculate the square notation for the current square starting from the top left corner (h1, g1, f1, ..., a1, h2, g2, ..., a8)
            square_notation = string.ascii_lowercase[num_of_squares - k - 1] + str(
                int(i / square_size) + 1
            )

            # Calculate the difference between the two squares
            diff = cv2.absdiff(prev_img_square, cur_img_square)

            # Calculate the confidence rate of the difference
            confidence_rate = np.sum(diff) / (square_size * square_size)  # type: ignore

            k += 1  # Incrementing the counter for x coordinates

            # Iterate through the moves list and save the sorted moves in terms of confidence rate
            for z in range(0, max_num_of_moves):
                # Check if the confidence rate is greater than the confidence rate in the list
                if confidence_rate >= confidence_rate_list[z]:
                    confidence_rate_list.insert(
                        z, confidence_rate
                    )  # Save the confidence rate

                    moves_list.insert(z, square_notation)  # Save the square notation

                    confidence_rate_list.pop()  # Remove the last element in the list
                    moves_list.pop()  # Remove the last element in the list
                    break  # Break out of the loop

    # Create a threshold for the confidence rate based on the maximum confidence rate
    threshold = confidence_rate_list[0] * 0.4

    # Iterate through the confidence rate list
    for i in range(len(confidence_rate_list) - 1, -1, -1):
        # Check if the confidence rate is less than the threshold
        if confidence_rate_list[i] < threshold:
            confidence_rate_list.pop(i)  # Remove the confidence rate from the list
            moves_list.pop(i)  # Remove the move from the list

    # Check if no moves were found
    if confidence_rate_list == [0 for _ in range(max_num_of_moves)]:
        return (None, None)  # Return None if no moves were found

    # Round the confidence rates to two decimal places
    confidence_rate_list = [
        round(confidence_rate, 2) for confidence_rate in confidence_rate_list  # type: ignore
    ]

    print("Confidence rates:")
    print(confidence_rate_list)  # Test

    return (
        moves_list,
        confidence_rate_list,
    )  # Return the moves list and the confidence rate list


def cv2_to_tk(img: np.ndarray):
    """
    Convert an OpenCV image (BGR format) to a Tkinter PhotoImage object (RGB format).

    Parameters:
    -   img (np.ndarray): The input OpenCV image.

    Returns:
    -   tk_img (Tkinter.PhotoImage): The converted Tkinter PhotoImage object.
    """

    # Flip the image vertically
    img = cv2.flip(img, 0)

    # Convert the Image to RGB format
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Convert the Image object into a TkPhoto object
    img_arr = Image.fromarray(img)
    tk_img = ImageTk.PhotoImage(image=img_arr)

    return tk_img  # Return the TkPhoto object


def flip_img(img: np.ndarray, flip: bool):
    """
    Flip an image horizontally and vertically, if needed.

    Parameters:
    -   img (np.ndarray): The input image.

    Returns:
    -   img (np.ndarray): The flipped image.
    """

    if flip:
        img = cv2.flip(img, 1)
        img = cv2.flip(img, 0)

    return img  # Return the flipped image


def find_chessboard_corners(img: np.ndarray, square_size_offset: int = 0):
    """
    Finds the corners of the chessboard in an image.

    Args:
    -   img (np.ndarray): The image of the chessboard.
    -   square_size_offset (int): The offset to be added to the size of each square in the chessboard. Defaults to 0.

    Returns:
    -   list: A list containing the coordinates of the corners of the chessboard, or None if the corners were not found.
    """

    square_size = int(
        img_resolution[0] / num_of_squares + square_size_offset
    )  # Size of each square in the chessboard plus the offset

    # Find the corners of the chessboard
    _, corners = cv2.findChessboardCorners(
        img,  # type: ignore
        board_pattern_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )  # type: ignore

    # Check if the corners were found
    if corners is None:
        return None

    # Initialize the corners list
    corners_list = []

    # Iterate through the corners
    for corner in corners:
        # Calculate the corner coordinates
        corner_coordinates = [
            int(corner[0][0]),
            int(corner[0][1]),
        ]

        corners_list.append(corner_coordinates)  # Save the corner coordinates

    # Add the offset to the corners
    for corner in corners_list:
        corner[0] -= square_size
        corner[1] -= square_size

    return corners_list  # Return the corners list


def find_x_y_offsets(corners_list: list, square_size_offset: int = 0):
    """
    Calculates the x and y coordinates offsets between the 0,0 point and the outer corner with the minimum distance.

    Args:
    -   corners_list (list): A list of corners represented as (x, y) coordinates.

    Returns:
    -   tuple: A tuple containing the x and y coordinates offsets.
    """

    # Initialize the distances list
    distances_list = []

    # Find the distance between the 0,0 point and the outer corners
    for corner in corners_list:
        distance = np.sqrt(corner[0] ** 2 + corner[1] ** 2)
        distances_list.append(distance)

    # Find the index of the minimum distance
    min_distance_index = distances_list.index(min(distances_list))

    # Find the x and y coordinates offsets between the 0,0 point and the outer corner with the minimum distance
    x_offset = corners_list[min_distance_index][0]
    y_offset = corners_list[min_distance_index][1]

    square_size = int(
        img_resolution[0] / num_of_squares + square_size_offset
    )  # Size of each square in the chessboard plus the offset

    x_offset = (square_size / 2) + x_offset  # Offset to adjust the x coordinate offset

    y_offset = (square_size / 2) + y_offset  # Offset to adjust the y coordinate offset

    return int(x_offset), int(
        y_offset
    )  # Return the int values of the x and y coordinates offsets


def find_squares_coordinates(
    corners_list: list,
    square_size_offset: int = 0,
    column_offset: int = 0,
    row_offset: int = 0,
):
    """
    Find the coordinates of each square in a chessboard.

    Args:
    -   corners_list (list): List of corner coordinates of the chessboard.
    -   square_size_offset (int, optional): Offset to adjust the size of each square. Defaults to 0.
    -   column_offset (int, optional): Offset to adjust the distance between columns. Defaults to 0.

    Returns:
    -   dict: Dictionary containing the coordinates of each square in centimeters.
    """

    square_size = int(
        img_resolution[0] / num_of_squares + square_size_offset
    )  # Size of each square in the chessboard plus the offset

    # Find the x and y coordinates offsets between the 0,0 point and the outer corner with the minimum distance
    x_offset, y_offset = find_x_y_offsets(corners_list, square_size_offset)

    # Initialize the square coordinates in pixels dictionary
    square_coordinates_px = {}

    # Find the middle points for every square in the chessboard

    ii = 0  # Initializing a counter for each row
    for i in range(
        int(y_offset), (square_size * num_of_squares) + int(y_offset), square_size
    ):  # Iterate through rows
        jj = 0  # Initializing a counter for each row
        for j in range(
            int(x_offset), (square_size * num_of_squares) + int(x_offset), square_size
        ):  # Iterate through columns
            # Calculate the square notation for the current square starting from the top right corner (h1, g1, f1, ..., a1, h2, g2, ..., a8)
            square_notation = string.ascii_lowercase[num_of_squares - jj - 1] + str(
                int((i - y_offset) / square_size) + 1
            )

            # Save the square notation and the middle point of the square
            square_coordinates_px[square_notation] = (
                (j + (jj * column_offset)),
                (i + (ii * row_offset)),
            )

            jj += 1  # Incrementing the counter for x coordinates

        ii += 1  # Incrementing the counter for y coordinates

    # Initialize the square coordinates in cm dictionary
    square_coordinates_cm = {}

    # Find the square coordinates (x,y,z) in cm
    for square_notation, square_coordinate in square_coordinates_px.items():
        square_coordinates_cm[square_notation] = (
            round(square_coordinate[0] * pixel_2_cm_ratio, 3),  # x coordinate
            round(square_coordinate[1] * pixel_2_cm_ratio, 3),  # y coordinate
            0.0,  # z coordinate
        )

    return square_coordinates_cm  # Return the square coordinates in cm


def cam_2_arm_transformation(square_coordinates: dict):
    """
    Transforms the camera coordinates of an object to the base frame coordinates.

    Args:
    -   camera_coordinates (tuple): The camera coordinates of the object in pixel units.

    Returns:
    -   numpy.ndarray: The coordinates of the object in the base frame.
    """
    # Initial rotation angle of the camera frame in degrees
    rot_angle_x = pi
    rot_angle_y = 0
    rot_angle_z = pi / 2
    # Initial rotation angle of the camera frame in degrees

    base_frame_coordinates = {}  # Initialize the base frame coordinates dictionary

    # Define the rotation matrices (x,y,z) from coordinate frame of the camera frame to the base frame
    rotation_matrix_x = np.array(
        [
            [1, 0, 0],
            [0, np.cos(rot_angle_x), -np.sin(rot_angle_x)],
            [0, np.sin(rot_angle_x), np.cos(rot_angle_x)],
        ]
    )

    rotation_matrix_y = np.array(
        [
            [np.cos(rot_angle_y), 0, np.sin(rot_angle_y)],
            [0, 1, 0],
            [-np.sin(rot_angle_y), 0, np.cos(rot_angle_y)],
        ]
    )

    rotation_matrix_z = np.array(
        [
            [np.cos(rot_angle_z), -np.sin(rot_angle_z), 0],
            [np.sin(rot_angle_z), np.cos(rot_angle_z), 0],
            [0, 0, 1],
        ]
    )

    # Multiply the rotation matrices to get the rotation matrix from the camera frame to the base frame
    rotation_matrix = rotation_matrix_z @ rotation_matrix_y @ rotation_matrix_x

    displacment_x = 20.5  # Displacment of the camera frame in the x direction in cm
    displacment_y = 36.0  # Displacment of the camera frame in the y direction in cm
    displacment_z = 0.0  # Displacment of the camera frame in the z direction in cm

    # Define the translation vector from coordinate frame of the camera frame to the base frame
    translation_vector = np.array(
        [
            [displacment_x],
            [displacment_y],
            [displacment_z],
        ]
    )

    # Row vector for bottom of homogeneous transformation matrix
    homogeneous_vector = np.array(
        [
            [
                0.0,
                0.0,
                0.0,
                1.0,
            ]
        ]
    )

    # Create the homogeneous transformation matrix from the coordinate frame of the camera frame to the base frame
    homogeneous_matrix = np.concatenate(
        (rotation_matrix, translation_vector), axis=1
    )  # Concatenate the rotation matrix and the translation vector
    homogeneous_matrix = np.concatenate(
        (homogeneous_matrix, homogeneous_vector), axis=0
    )  # Concatenate the homogeneous matrix and the homogeneous row

    # Loop through the squares using the key value pairs
    for square_notation, square_coordinate in square_coordinates.items():
        # Initialize the coordinates in the robotic base frame
        base_frame_coordinate = np.array([[0.0], [0.0], [0.0], [1.0]])

        # Coordinates of the square in the camera reference frame in cm
        x2_cm = square_coordinate[0]
        y2_cm = square_coordinate[1]
        z2_cm = square_coordinate[2]

        cam_frame_coordinates = np.array(
            [
                [x2_cm],
                [y2_cm],
                [z2_cm],
                [1],
            ]
        )

        # Multiply the homogeneous transformation matrix by the coordinates of the square in the camera reference frame
        # to get the coordinates of the square in the base frame
        base_frame_coordinate = homogeneous_matrix @ cam_frame_coordinates
        # Add the coordinates of the square in the base frame to the base frame coordinates dictionary
        base_frame_coordinates[square_notation] = (
            round(base_frame_coordinate[0][0], 3),
            round(base_frame_coordinate[1][0], 3),
            round(base_frame_coordinate[2][0], 3),
        )

    return base_frame_coordinates  # Return the base frame coordinates dictionary
