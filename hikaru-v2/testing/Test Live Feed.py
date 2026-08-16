import cv2

ip = "http://10.1.95.223:8080/video"

cam_id = 0

# cam = cv2.VideoCapture(ip)
cam = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)

# i = 0

while True:
    ret, frame = cam.read()

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # k = cv2.waitKey(0)

    # if k == ord("q"):
    #     break

    # # Check if the user wants to save the image
    # elif k == ord("s"):
    #     cv2.imwrite(f"./Test/Live Img {i}.jpg", frame)
    #     print(f"Image {i} saved")
    #     i += 1

cam.release()
