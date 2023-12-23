import cv2
import numpy as np
import string
from PIL import Image, ImageTk

board_pattern_size = (
    7,
    7,
)  # Number of squares in a row/column of the chessboard to be detected
img_resolution = (400, 400)  # Resolution of the images to be used


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


def show_img(
    img: np.ndarray, window_name: str, image_resolution: tuple = img_resolution
):
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
    Takes a 640x480 picture using the camera, then returns it as a numpy array.

    Args:
    -   cam (cv2.VideoCapture): The camera object.

    Returns:
    -   img (numpy.ndarray): The image as a numpy array.

    Raises:
    -   Exception: If the picture could not be taken.
    """

    # Take picture
    result, img = cam.read()

    # If the picture could not be taken, raise an exception
    if not result:
        raise Exception("Could not take picture")

    return img  # Return the image


def read_img(path: str):
    """
    Reads an image from a file and returns it as a numpy array.

    Args:
    -   path (str): The path to the image file.

    Returns:
    -   img: The image as a numpy array.

    Raises:
    -   Exception: If the image could not be read.
    """
    img = cv2.imread(path)

    if img is None:
        raise Exception("Could not read image")

    return img


def get_homography_matrix(img: np.ndarray, motherboard_path: str):
    """
    Finds the homography matrix between the current image of the board and the reference board image

    Args :
    -   img (ndarray) : The current image of the full chess board in BGR color format
    -   motherboard_path (str) : The path to the reference board image

    Returns :
    -   homography_matrix (ndarray) : Homography matrix

    Raises :
    -   Exception : If the chessboard corners were not found in either image
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
        motherboard, cv2.COLOR_BGR2HSV
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
        raise Exception("Could not find chessboard corners")


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
    -   tuple: A tuple containing the moves list and the confidence rate list.
    """
    num_of_squares = 8  # Number of squares in a row/column of the chessboard
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
        for j in range(
            0, num_of_squares * square_size, square_size
        ):  # Iterate through columns
            prev_img_square = prev_img[
                i : i + square_size, j : j + square_size
            ]  # Get the square from the previous image
            cur_img_square = cur_img[
                i : i + square_size, j : j + square_size
            ]  # Get the square from the current image

            # Calculate the square notation
            square_notation = string.ascii_lowercase[int(j / square_size)] + str(
                num_of_squares - int(i / square_size)
            )

            # Calculate the difference between the two squares
            diff = cv2.absdiff(prev_img_square, cur_img_square)

            # Calculate the confidence rate of the difference
            confidence_rate = np.sum(diff) / (square_size * square_size)  # type: ignore

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
    threshold = confidence_rate_list[0] * 0.25

    # Iterate through the confidence rate list
    for i in range(len(confidence_rate_list) - 1, -1, -1):
        # Check if the confidence rate is less than the threshold
        if confidence_rate_list[i] < threshold:
            confidence_rate_list.pop(i)  # Remove the confidence rate from the list
            moves_list.pop(i)  # Remove the move from the list

    # Check if no moves were found
    if confidence_rate_list == [0 for _ in range(max_num_of_moves)]:
        moves_list = None  # Set the moves list to None

    # Round the confidence rates to two decimal places
    confidence_rate_list = [
        round(confidence_rate, 2) for confidence_rate in confidence_rate_list
    ]

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
    if not flip:
        img = cv2.flip(img, 1)
        img = cv2.flip(img, 0)

    return img  # Return the flipped image


def find_squares_coordinates(img: np.ndarray):
    """
    Finds the corners of the chessboard in an image.

    Args:
    -   img (np.ndarray): The image of the chessboard.

    Returns:
    -   list: A list containing the coordinates of the corners of the chessboard.

    Raises:
    -   Exception: If the corners of the chessboard could not be found.
    """
    num_of_squares = 8  # Number of squares in a row/column of the chessboard
    square_size = int(
        img_resolution[0] / num_of_squares - 7
    )  # Size of each square in the chessboard

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
        raise Exception("Could not find chessboard corners")

    # Initialize the corners list
    corner_coordinates_list = []

    # Initialize the outer corners list
    outer_corners_list = []

    # Iterate through the corners
    for corner in corners:
        # Calculate the corner coordinates
        corner_coordinates = [
            int(corner[0][0]),
            int(corner[0][1]),
        ]

        corner_coordinates_list.append(
            corner_coordinates
        )  # Save the corner coordinates

    modified_img = (
        img.copy()
    )  # Copy the image to a new variable to avoid modifying the original image # Test

    # Draw the corners on the modified image # Test
    for corner in corner_coordinates_list:
        cv2.circle(modified_img, (corner[0], corner[1]), 2, (0, 0, 255), 2)

    show_img(modified_img, "modified img with all corners", modified_img.shape)  # Test

    # Find the outer corners of the chessboard using the combination of the minimum and maximum x and y coordinates
    outer_corners_list.append(
        [
            min(corner_coordinates_list, key=lambda x: x[0])[0],  # type: ignore
            min(corner_coordinates_list, key=lambda x: x[1])[1],  # type: ignore
        ]
    )  # Save the top left corner

    outer_corners_list.append(
        [
            max(corner_coordinates_list, key=lambda x: x[0])[0],  # type: ignore
            min(corner_coordinates_list, key=lambda x: x[1])[1],  # type: ignore
        ]
    )  # Save the top right corner

    outer_corners_list.append(
        [
            min(corner_coordinates_list, key=lambda x: x[0])[0],  # type: ignore
            max(corner_coordinates_list, key=lambda x: x[1])[1],  # type: ignore
        ]
    )  # Save the bottom left corner

    outer_corners_list.append(
        [
            max(corner_coordinates_list, key=lambda x: x[0])[0],  # type: ignore
            max(corner_coordinates_list, key=lambda x: x[1])[1],  # type: ignore
        ]
    )  # Save the bottom right corner

    print("Outer corners list:")
    print(outer_corners_list)

    modified_img = (
        img.copy()
    )  # Copy the image to a new variable to avoid modifying the original image # Test

    # Draw the outer corners on the modified image # Test
    for outer_corner in outer_corners_list:
        cv2.circle(modified_img, (outer_corner[0], outer_corner[1]), 2, (0, 0, 255), 2)

    show_img(
        modified_img, "modified img with outer corners", modified_img.shape
    )  # Test

    # Add the offset to the outer corners
    outer_corners_list[0][0] -= square_size
    outer_corners_list[0][1] -= square_size

    outer_corners_list[1][0] += square_size
    outer_corners_list[1][1] -= square_size

    outer_corners_list[2][0] -= square_size
    outer_corners_list[2][1] += square_size

    outer_corners_list[3][0] += square_size
    outer_corners_list[3][1] += square_size

    print("Outer corners list with offset:")
    print(outer_corners_list)

    modified_img = (
        img.copy()
    )  # Copy the image to a new variable to avoid modifying the original image # Test

    # Draw the outer corners on the modified image # Test
    for outer_corner in outer_corners_list:
        cv2.circle(modified_img, (outer_corner[0], outer_corner[1]), 2, (0, 0, 255), 2)

    show_img(
        modified_img, "modified img with outer corners and offset", modified_img.shape
    )  # Test

    # Find the distance between the 0,0 point and the outer corners
    distances_list = []

    for outer_corner in outer_corners_list:
        distance = np.sqrt(outer_corner[0] ** 2 + outer_corner[1] ** 2)
        distances_list.append(distance)

    print("Distances:")
    print(distances_list)

    # Find the index of the minimum distance
    min_distance_index = distances_list.index(min(distances_list))

    print("Min distance index:")
    print(f"distances[{min_distance_index}] = {distances_list[min_distance_index]}")

    modified_img = (
        img.copy()
    )  # Copy the image to a new variable to avoid modifying the original image # Test

    # Draw a line from the 0,0 point to the outer corner with the minimum distance # Test
    cv2.line(
        modified_img,
        (0, 0),
        (
            outer_corners_list[min_distance_index][0],
            outer_corners_list[min_distance_index][1],
        ),
        (0, 0, 255),
        2,
    )

    # Draw a circle at the 0,0 point # Test
    cv2.circle(modified_img, (0, 0), 2, (0, 0, 255), 2)

    # Draw a circle at the outer corner with the minimum distance # Test
    cv2.circle(
        modified_img,
        (
            outer_corners_list[min_distance_index][0],
            outer_corners_list[min_distance_index][1],
        ),
        2,
        (0, 0, 255),
        2,
    )

    show_img(modified_img, "modified img with line", modified_img.shape)  # Test

    # Find the x and y coordinates offsets between the 0,0 point and the outer corner with the minimum distance
    x_offset = outer_corners_list[min_distance_index][0]
    y_offset = outer_corners_list[min_distance_index][1]

    # Find the middle points of the squares in the chessboard
    square_coordinates = {}

    # Find the middle points for every square in the chessboard
    for i in range(
        y_offset, (square_size * num_of_squares) + y_offset, square_size
    ):  # Iterate through rows
        k = 0  # Initializing a counter for x coordinates

        for j in range(
            x_offset, (square_size * num_of_squares) + x_offset, square_size
        ):
            square_notation = string.ascii_lowercase[
                int((j - x_offset) / square_size)
            ] + str(num_of_squares - int((i - y_offset) / square_size))

            square_coordinates[square_notation] = (
                j + int(square_size / 2) + (k * 2),
                i + int(square_size / 2),
            )

            k += 1  # Incrementing the counter for x coordinates

    print("Square coordinates:")
    print(square_coordinates)

    modified_img = (
        img.copy()
    )  # Copy the image to a new variable to avoid modifying the original image # Test

    # Draw the middle points on the modified image # Test
    for square_coordinate in square_coordinates.values():
        cv2.circle(
            modified_img,
            (square_coordinate[0], square_coordinate[1]),
            2,
            (0, 0, 255),
            2,
        )

    show_img(modified_img, "modified corners", modified_img.shape)  # Test

    return outer_corners_list  # Return the corners list
