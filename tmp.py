import cv2
import utility

util = utility.Utility()

cv2.namedWindow("TMP")
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cam.set(cv2.CAP_PROP_FPS, 144)
running = cam.isOpened()

while running:
    running, frame = cam.read()

    aux_fps = util.fps_counter(True)

    if aux_fps != "":
        print(aux_fps)
        fps = aux_fps

    cv2.putText(frame, fps, (7, 70),
       cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow("TMP", frame)

    if cv2.waitKey(20) == 27:
        break

cam.release()
cv2.destroyAllWindows()
