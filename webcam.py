import cv2
import numpy as np
import log
import singleton
import time
import utility
import configs
import image_recognition
import UI

class WebcamCapture(metaclass=singleton.Singleton):    
    name = ""
    logger = None
    cam = None
    running = False
    thread_running = True
    window_created = False
    img_rec = None
    util = None
    config = None
    ui = None

    def __init__(self, name = "Camera"):
        self.img_rec = image_recognition.ImageRecognition()
        self.logger = log.Logger()
            
        self.util = utility.Utility()
        self.config = configs.Configs()
        self.name = name
        self.ui = UI.UI()

    def init(self):
        if self.running: return 0

        retrieve = True

        while retrieve and self.thread_running:
            try:
                if self.window_created == False:
                    cv2.namedWindow(self.name)
                self.window_created = True
                self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
                self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                self.cam.set(cv2.CAP_PROP_FPS, 144)
                self.running = self.cam.isOpened()
                retrieve = False
                
                if self.cam == None or not self.running:
                    print("\tWebcam device busy! Close any unwanted apps using the camera! Retrying...")
                    retrieve = True
                    time.sleep(1)
            
            except Exception as err:
                self.logger.log(log.SEVERITY.FATAL,
                    "Could not initialize the webcam capture device...", err)
                return 1

        return 0    

    def capture(self):
        sanity = True
        fps = 0
        
        while sanity and self.thread_running:
            if self.running:
                self.running, frame = self.cam.read()

            while self.thread_running and cv2.countNonZero(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) == 0:
                print("\tWebcam device is missing! Add a new camera to the machine! Retrying...")
                time.sleep(1)
                self.close_device(False)
                self.init()
                self.running, frame = self.cam.read()            
        
            while self.running and self.thread_running:
                try:
                    aux_fps = self.util.fps_counter(True)

                    if aux_fps != "":
                        fps = aux_fps

                    width_resize = self.config.config["imgWidth"]
                    height_resize = self.config.config["imgHeight"]

                    if width_resize < 256:
                        width_resize = 256

                    if height_resize < 144:
                        height_resize = 144

                    gui_frame = None

                    if self.config.config["windowMode"] == "advanced":
                        frame = cv2.resize(frame, (width_resize, height_resize * 2))
                        gui_frame = np.zeros((height_resize, width_resize* 2, 3), np.uint8)
                    elif self.config.config["windowMode"] == "complex":
                        frame = cv2.resize(frame, (width_resize, height_resize))
                        gui_frame = np.zeros((height_resize, width_resize, 3), np.uint8)
                    else:
                        frame = cv2.resize(frame, (width_resize * 2, height_resize * 2))
                        gui_frame = np.zeros((height_resize * 2, width_resize* 2, 3), np.uint8)

                    blur, color_frame, edges, objects = self.img_rec.get_image_objects(frame,
                        self.config.config["RGBMin"], self.config.config["RGBMax"],
                        self.config.config["edgeThresholdMin"], self.config.config["edgeThresholdMax"],
                        self.config.config["edgeBlurKernelSize"], self.config.config["edgeBlurKernelSigma"],
                        self.config.config["imgObjectBoxMinWidth"], self.config.config["imgObjectBoxMaxWidth"],
                        self.config.config["imgObjectBoxMinHeight"], self.config.config["imgObjectBoxMaxHeight"])

                    for item in objects:
                        start = (item[0], item[1])
                        end = (item[2] + item[0], item[3] + item[1])

                        frame = cv2.rectangle(frame, start, end, (self.config.config["RGBMin"][2], 0, self.config.config["RGBMin"][0]), 2)

                    # Display FPS:
                    cv2.putText(frame, fps, (7, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

                    # Display image based text only once
                    if self.config.config["displayFrameText"] == "on":
                        cv2.putText(blur, "NOISE SMOOTHING", (7, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 50), 3, cv2.LINE_AA)

                        cv2.putText(color_frame, "COLOR DETECTION", (7, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 50), 3, cv2.LINE_AA)

                        cv2.putText(edges, "CANNY EDGE DETECTION", (7, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 50), 3, cv2.LINE_AA)
                    
                    output_frame = frame

                    self.ui.update(gui_frame)
                    self.ui.gui(gui_frame)

                    if self.config.config["windowMode"] == "advanced":
                        output_frame = np.hstack((frame, color_frame))
                        cv2.line(output_frame, (width_resize - 1, 0),
                                (width_resize - 1, height_resize * 2), (100, 22, 150), 2)
                    elif self.config.config["windowMode"] == "complex":
                        tmp_first_row_frame = np.hstack((gui_frame, frame))
                        tmp_second_row_frame = np.hstack((color_frame, edges))
                        cv2.line(tmp_second_row_frame, (0, 0),
                                (width_resize * 2, 0), (100, 22, 150), 2)
                        output_frame = np.vstack((tmp_first_row_frame, tmp_second_row_frame))
                        cv2.line(output_frame, (width_resize - 1, 0),
                                (width_resize - 1, height_resize * 2), (100, 22, 150), 2)

                    self.ui.update_context()
                    cv2.imshow(self.name, output_frame)                    
                    self.running, frame = self.cam.read()

                    if cv2.waitKey(20) == 27:
                        break

                except Exception as err:
                    sanity = False
                    self.running = False
                    self.logger.log(log.SEVERITY.FATAL,
                        "Camera capture operation suddenly crushed...", err)
                    self.close_device()

            #Code that attempts to recover a failed camera device
            if self.running == False and self.thread_running == True and sanity == True:
                print("\tWebcam device suddenly crushed/disconnected! Retrying...")
                time.sleep(1)
                self.close_device(False)
                self.init()
            else:
                sanity = False

        self.running = False
        return 0

    def close_device(self, window = True):
        self.running = False
        self.thread_running = True

        if self.cam != None:
            self.cam.release()

        if window == True:
            cv2.destroyAllWindows()
            #cv2.destroyWindow(self.name)
            self.window_created = False

    def clear(self):
        print("\t\t-clearing WEBCAM data from memory...")
        self.close_device()
