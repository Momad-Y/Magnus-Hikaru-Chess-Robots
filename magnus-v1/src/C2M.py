import cv2
import numpy as np
import string

try:
    from picamera.array import PiRGBArray  # type: ignore
    from picamera import PiCamera  # type: ignore
except:
    print("Camera Error")
    cap = -1
    pass
else:
    try:
        cap = PiCamera()
    except:
        print("Camera Error")
        cap = -1


patternSize = (7, 7)
cbPatternPath = "static/img/cbPattern.jpg"
imgSize = (400, 400)
picResolution = (640, 480)


def showImg(img, windowName):
    """
    Brief : Show an image

    Args :
        img (ndarray) : An image

        windowName (string) : Name of the window
    """

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName, picResolution[0], picResolution[1])
    cv2.imshow(windowName, img)
    cv2.waitKey(0)


def findHomography(img):
    """
    Brief : Finds the homography matrix between an image of the current board and an image of the ideal board positions

    Args :
        img (ndarray) : The current image of the empty chess board in BGR color format

    Returns :
        homography (ndarray) : Homography matrix between frame and cbPattern
    """

    cbPattern = cv2.imread(cbPatternPath)
    imgCorners = img.copy()

    print("Calibrating the board")

    # Color-segmentation to get binary mask
    lwrImg = np.array([0, 0, 143])
    uprImg = np.array([179, 61, 252])
    hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mskImg = cv2.inRange(hsvImg, lwrImg, uprImg)

    lwrCbP = np.array([0, 0, 143])
    uprCbP = np.array([179, 61, 252])
    hsvCbP = cv2.cvtColor(cbPattern, cv2.COLOR_BGR2HSV)
    mskCbP = cv2.inRange(hsvCbP, lwrCbP, uprCbP)

    # Extract chess-board
    krnImg = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 30))
    dltImg = cv2.dilate(mskImg, krnImg, iterations=5)
    resImg = 255 - cv2.bitwise_and(dltImg, mskImg)

    krnCbP = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 30))
    dltCbP = cv2.dilate(mskCbP, krnCbP, iterations=5)
    resCbP = 255 - cv2.bitwise_and(dltCbP, mskCbP)

    # Displaying chessboards features
    resImg = np.uint8(resImg)

    resCbP = np.uint8(resCbP)

    # Find chessboards corners
    retImg, cornersImg = cv2.findChessboardCorners(
        resImg,
        patternSize,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )

    retCbp, cornersCbP = cv2.findChessboardCorners(
        resCbP,
        patternSize,
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_FAST_CHECK
        + cv2.CALIB_CB_NORMALIZE_IMAGE,
    )

    # Find the transformation/homography matrix between the cbPattern and the image
    if retImg and retCbp:
        print("Camera calibration successful")

        homography, _ = cv2.findHomography(cornersImg, cornersCbP, cv2.RANSAC, 5.0)

        showImg(
            cv2.drawChessboardCorners(imgCorners, patternSize, cornersImg, retImg),
            "Corners detected for the image",
        )

        return homography
    else:
        print("Can not detect borders")
        return -1


def applyHomography(img, H):
    """
    Brief : Warps the current image of the board

    Args :
        img (ndarray) : The current image of the full chess board in BGR color format

        H (ndarray) : Homography matrix

    Returns :
        imgNEW (ndarray) : Warped image of the full chess board
    """

    print("Applying the calibration")

    imgNew = cv2.warpPerspective(img, H, imgSize)

    return imgNew


def findMoves(img1, img2):
    """
    Brief : Finds the chess board moves of the most changed 4, 3 or 2 squares

    Args :
        img1 (ndarray) : The Rotated warped image of the full chess board before the moves was played

        img2 (ndarray) : The Rotated warped image of the full chess board after the moves was played

    Returns :
        moves (array) : Chess board moves of the most squares

        confidenceRate (array): Confidence rate for each move
    """

    print("Finding the played move")

    size = 50
    img1Sq = img2Sq = []
    confidenceRate = [0, 0, 0, 0]
    moves = [0, 0, 0, 0]

    # Looping on each chessboard square in a cropped 400x400 images
    for y in range(0, 8 * size, size):
        for x in range(0, 8 * size, size):
            img1Sq = img1[x : x + size, y : y + size]
            img2Sq = img2[x : x + size, y : y + size]

            # Calculating the absolute norm for each square from img1 & img 2
            dist = cv2.norm(img2Sq, img1Sq)

            for z in range(0, 4):
                if dist >= confidenceRate[z]:
                    confidenceRate.insert(z, dist)

                    # Save in algebraic chess notation
                    moves.insert(
                        z,
                        (
                            string.ascii_lowercase[int(x / size)]
                            + str(int(y / size + 1))
                        ),
                    )

                    confidenceRate.pop()
                    moves.pop()
                    break

    # Make threshold with a percentage of the change in color of the Largest two changes
    thresh = (confidenceRate[0] + confidenceRate[1]) / 2 * (0.5)

    for t in range(3, 1, -1):
        if confidenceRate[t] < thresh:
            moves.pop()

    return moves, confidenceRate


def takePic():
    """
    Brief : Takes a 640x480 picture in bgr format

    Returns :
        frame (ndarray) : Picture taken
    """

    print("Taking a picture")

    if cap == -1:
        print("RPi camera module not found or camera not found")
        return -1
    else:
        cap.resolution = picResolution
        rawCapture = PiRGBArray(cap, size=picResolution)

    cap.capture(rawCapture, format="bgr")
    frame = rawCapture.array

    rawCapture.truncate(0)  # Clear the stream in preparation for the next image

    return frame


def demo():
    print("Starting")

    prevImg = takePic()  # Empty chessboard image

    showImg(prevImg, "Empty chessboard image")

    homography = findHomography(prevImg)

    showImg(applyHomography(prevImg, homography), "Empty chessboard image warped")

    print("Place the pieces on the board, Do not move the board")

    prevImg = takePic()  # Full chessboard image

    showImg(prevImg, "Full chessboard image")

    prevImg = applyHomography(prevImg, homography)

    showImg(prevImg, "Full chessboard image warped")

    print("Play you move, Do not move the board")

    curImg = takePic()  # Full chessboard image after the move

    showImg(curImg, "Full chessboard image after a move")

    curImg = applyHomography(curImg, homography)

    showImg(curImg, "Full chessboard image after a move warped")

    moves, confidenceRate = findMoves(prevImg, curImg)

    confidenceRateRound = [round(x, 2) for x in confidenceRate]

    return moves, confidenceRateRound
