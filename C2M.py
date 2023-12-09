import cv2
import numpy as np
import string

board_pattern_size = (
    7,
    7,
)  # Number of squares in a row/column of the chessboard to be detected
img_resolution = (400, 400)  # Resolution of the images to be used
pic_resolution = (640, 480)  # Resolution of the pictures to be taken


def show_img(img: np.ndarray, window_name: str):
    """
    Display an image in a named window.

    Args:
    -   img (numpy.ndarray): The image to be displayed.
    -   window_name (str): The name of the window.

    Returns:
    -   None
    """
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, pic_resolution[0], pic_resolution[1])
    cv2.imshow(window_name, img)
    cv2.waitKey(0)


def take_img(cam: cv2.VideoCapture):
    """
    Takes a 640x480 picture using the camera, then returns it as a numpy array.

    Args:
    -   None

    Returns:
    -   img: The captured image as a numpy array.

    Raises:
    -   Exception: If the picture could not be taken.
    """
    # Set camera resolution to 640x480
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, pic_resolution[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, pic_resolution[1])

    # Take picture
    result, img = cam.read()

    if not result:
        raise Exception("Could not take picture")

    return img


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
    )  # Get the board's image mask without the background

    motherboard_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (50, 30)
    )  # Kernel for the mask of the reference board image

    dilated_motherboard_kernel = cv2.dilate(
        motherboard_mask, motherboard_kernel, iterations=5
    )  # Dilate the mask of the reference board image to get the full board

    result_motherboard = 255 - cv2.bitwise_and(
        dilated_motherboard_kernel, motherboard_mask
    )  # Get the mask of the reference board image without the background

    # Convert the images to uint8 format
    result_img = np.uint8(result_img)
    result_motherboard = np.uint8(result_motherboard)

    return_img, img_corners = cv2.findChessboardCorners(
        result_img,
        board_pattern_size,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )  # Find the corners of the chessboard in the image

    return_motherboard, motherboard_corners = cv2.findChessboardCorners(
        result_motherboard,
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


def warp_img(img: np.ndarray, homography_matrix: np.ndarray):
    """
    Applies a perspective transformation to the input image using the provided homography matrix.

    Args:
    -   img (np.ndarray): The input image to be warped.
    -   homography_matrix (np.ndarray): The homography matrix defining the transformation.

    Returns:
    -   np.ndarray: The warped image.
    """
    return cv2.warpPerspective(img, homography_matrix, img_resolution)


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
            confidence_rate = np.sum(diff) / (square_size * square_size)

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
    threshold = confidence_rate_list[0] * 0.7

    # Iterate through the confidence rate list
    for i in range(0, max_num_of_moves):
        # Check if the confidence rate is less than the threshold
        if confidence_rate_list[i] < threshold:
            confidence_rate_list.pop(i)  # Remove the confidence rate from the list
            moves_list.pop(i)

    return (
        moves_list,
        confidence_rate_list,
    )  # Return the moves list and the confidence rate list
