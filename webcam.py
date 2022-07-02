import cv2
import numpy as np
import log
import singleton
import time
import utility
import configs
import image_recognition
import UI
import math

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
    width_resize = None
    height_resize = None
    frame = []
    gui_frame = []
    blur = []
    color_frame = []
    edges = []
    objects = []
    color_frame_ball = []
    edges_ball = []
    objects_ball = []
    color_frame_enemy = []
    edges_enemy = []
    objects_enemy = []
    inv_pi = 1/math.pi

    def __init__(self, name = "Camera"):
        self.img_rec = image_recognition.ImageRecognition()
        self.logger = log.Logger()
            
        self.util = utility.Utility()
        self.config = configs.Configs()
        self.name = name
        self.ui = UI.UI()

    def init(self):

        self.width_resize = self.config.config["imgWidth"] 
        self.height_resize = self.config.config["imgHeight"]

        if self.config.config["windowMode"] == "advanced":
            self.height_resize = self.height_resize * 2  
        if self.running: return 0

        retrieve = True #retrieve are ca scop sa ruleze doar o singura data functia init(self) (de mai sus) si sa tot incerce
        #functia init pana cand aceasta reuseste (ex daca nu am camera conectata, programul va continua sa incerce sa depisteze
        # camera pana cand aceasta va fi conectata)

        while retrieve and self.thread_running:
            try:
                if self.window_created == False:
                    cv2.namedWindow(self.name)
                self.window_created = True
                self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
                self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width_resize)
                self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height_resize)
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

    def max_rgb_filter(self,image):
        # split the image into its BGR components
        (B, G, R) = cv2.split(image)
        # find the maximum pixel intensity values for each
        # (x, y)-coordinate,, then set all pixel values less
        # than M to zero
        M = np.maximum(np.maximum(R, G), B)
        R[R < M] = 0
        G[G < M] = 0
        B[B < M] = 0
            
        # merge the channels back together and return the image
        return cv2.merge([B, G, R])

    def capture(self):  #asta e functia care face MAGIA (citeste im frame by frame + proceseaza pentru a extrace obiecte cu o anumita culoare/spectru de culori)
        sanity = True
        fps = 0


        #Linia 65 (sanity=True) + linia 74(while self.thread_running and cv2.countNonZero(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) == 0:)
        #verifica daca, in timpul rularii programului, camera a crapat/s-a deconectat de la USB si incearca sa reinitializeze captura de imagine, dupa ce o noua camera
        #sau aceeasi camera a fost reconectata (daca nu avem functia asta, programul crapa)
        while sanity and self.thread_running:
            if self.running: #verifica daca inca ruleaza programul (merge captura in sine)
                self.running, frame = self.cam.read() #functia cam.read() se duce la webcam si ia captureaza urmatorul frame, daca exista (programul are camera activa)

            while self.thread_running and cv2.countNonZero(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) == 0:
                #In acest while, self.thread_running mentine thread-ul specific in executie (in cazul de fata, thread-ul "capture" [def capture(self):])
                #Functia cv2.countNonZero(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) == 0 Ii dau frame-ul in nuante de gri si returneaza cati pixeli nu sunt 0
                print("\tWebcam device is missing! Add a new camera to the machine! Retrying...")
                time.sleep(1)
                self.close_device(False)
                self.init()
                self.running, frame = self.cam.read()   
                # Mai pe scurt, acest while, verifica daca programul captureaza imagine frame by frame, iar daca nu, semnaleaza eroare cum ca nu exista camera conectata         
        
            while self.running and self.thread_running: #Aici se intampla cu adevarat magia (detecteaza ceea ce vreau eu de pe fiecare frame in parte)
                try:
                    aux_fps = self.util.fps_counter(True) #Aici arat calculez FPS-ul

                    if aux_fps != "":
                        fps = aux_fps

                    #width_resize = len(frame[0]) #len(frame[0]) -> width   #self.config.config["imgWidth"] 
                    #height_resize = len(frame) #len(frame) -> height   #self.config.config["imgHeight"]
                    
                    # GUI FRAME SIZE
                    gui_frame = np.zeros((len(frame), len(frame[0]), 3), np.uint8)
                    alpha = 1 # Contrast control (1.0-3.0)
                    beta = 0 # Brightness control (0-100)
                    frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

                    #frame_filter = self.max_rgb_filter(frame)               #Filtrul care detecteaza valoarea maxima RGB si o "transmite" celorlalti pixeli de aceeasi culoare
                    frame_filter = frame
                    #print(frame)

                    #My team color
                    blur, color_frame, edges, objects = self.img_rec.get_image_objects(frame_filter,
                        self.config.config["boundRGBMin"], self.config.config["boundRGBMax"],
                        self.config.config["edgeThresholdMin"], self.config.config["edgeThresholdMax"],
                        self.config.config["edgeBlurKernelSize"], self.config.config["edgeBlurKernelSigma"],
                        self.config.config["imgObjectBoxMinWidth"], self.config.config["imgObjectBoxMaxWidth"],
                        self.config.config["imgObjectBoxMinHeight"], self.config.config["imgObjectBoxMaxHeight"])

                    #Ball color
                    blur_ball, color_frame_ball, edges_ball, objects_ball = self.img_rec.get_image_objects(frame_filter,
                        self.config.config["ballRGBMin"], self.config.config["ballRGBMax"],
                        self.config.config["edgeThresholdMin"], self.config.config["edgeThresholdMax"],
                        self.config.config["edgeBlurKernelSize"], self.config.config["edgeBlurKernelSigma"],
                        self.config.config["imgObjectBoxMinWidth"], self.config.config["imgObjectBoxMaxWidth"],
                        self.config.config["imgObjectBoxMinHeight"], self.config.config["imgObjectBoxMaxHeight"])

                    #Enemy team color
                    blur_enemy, color_frame_enemy, edges_enemy, objects_enemy = self.img_rec.get_image_objects(frame_filter,
                        self.config.config["unboundRGBMin"], self.config.config["unboundRGBMax"],
                        self.config.config["edgeThresholdMin"], self.config.config["edgeThresholdMax"],
                        self.config.config["edgeBlurKernelSize"], self.config.config["edgeBlurKernelSigma"],
                        self.config.config["imgObjectBoxMinWidth"], self.config.config["imgObjectBoxMaxWidth"],
                        self.config.config["imgObjectBoxMinHeight"], self.config.config["imgObjectBoxMaxHeight"])

                    #TO DO - Role color (GoalKeeper / STriker)

                    # Display image based text only once
                    if self.config.config["displayFrameText"] == "on":
                        cv2.putText(color_frame, "COLOR DETECTION", (7, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 50), 2, cv2.LINE_AA)

                        cv2.putText(edges, "CANNY EDGE DETECTION", (7, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 50), 2, cv2.LINE_AA)

                    # Display FPS:
                    cv2.putText(frame, fps, (7, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

                    self.frame = frame
                    self.color_frame = color_frame
                    self.edges = edges
                    self.objects = objects
                    self.gui_frame = gui_frame
                    self.blur = blur                               
                    self.running, frame = self.cam.read()

                    self.color_frame_ball = color_frame_ball
                    self.edges_ball = edges_ball
                    self.objects_ball = objects_ball

                    self.color_frame_enemy = color_frame_enemy
                    self.edges_enemy = edges_enemy
                    self.objects_enemy = objects_enemy

                    if cv2.waitKey(20) == 27:  #Wait for ESC to close the program
                        break

                except Exception as err:
                    sanity = False
                    self.running = False
                    self.logger.log(log.SEVERITY.FATAL, "Camera capture operation suddenly crushed...", err)
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

    def draw_frame(self):
        while self.thread_running:
            while self.running:
                output_frame = None
                if len(self.frame) == 0 or len(self.color_frame) == 0 or len(self.edges) == 0 \
                                or len(self.gui_frame) == 0 or len(self.color_frame_ball) == 0 \
                                    or len(self.color_frame_enemy) == 0 or len(self.edges_ball) == 0 \
                                        or len(self.edges_enemy) == 0 :
                    continue  
                
                #color_frame -> depistare culoare echipa mea (cea de pe Bound (1/2))
                #color_frame_ball -> depistare culoare minge (portocaliu)
                #color_frame_enemy -> depistare culoare echipa adversa 
                
                draw_color_frame = cv2.bitwise_or(self.color_frame, self.color_frame_enemy)
                draw_color_frame = cv2.bitwise_or(draw_color_frame, self.color_frame_ball)
                self.edges = cv2.bitwise_or(self.edges, self.edges_enemy)
                self.edges = cv2.bitwise_or(self.edges, self.edges_ball)
                objects = self.objects + self.objects_ball + self.objects_enemy 
                frame = self.frame.copy()

                #Aici printez coordonata centrului fiecarui box/contur/obiect depistat, pana la i=i+1
                font = cv2.FONT_HERSHEY_COMPLEX

                for item in objects:
                    #start = (item[0], item[1])
                    #end = (item[2] + item[0], item[3] + item[1])
                    #x = int(item[0] + item[2] * 0.5)
                    #y = int(item[1] + item[3] * 0.5)
                    #string = str(x) + " " + str(y) 
                    #cv2.putText(frame, string, (item[0], item[1]), font, 0.5, (0, 255, 0)) # text on remaining co-ordinates.
                    tmp_frame = self.frame.copy()
                    rect = cv2.minAreaRect(item[4])
                    box = cv2.boxPoints(rect) #Aici am coordonatele box-ului pe care il deseneaza programul cand gaseste culoare
                    box = np.int0(box)
                    start_point_orientation = (int(item[0] + item[2] * 0.5), int(item[1] + item[3] * 0.5))
                    center_color = tmp_frame[start_point_orientation[1] % self.config.config["imgHeight"],start_point_orientation[0] % self.config.config["imgWidth"]]
                    center_color = (int(center_color[0]), int(center_color[1]), int(center_color[2]))

                    cv2.drawContours(frame,[box],0,center_color,2)

                for item in self.objects:
                    tmp_frame = self.frame.copy()
                    rect = cv2.minAreaRect(item[4])
                    box = cv2.boxPoints(rect) #Aici am coordonatele box-ului pe care il deseneaza programul cand gaseste culoare
                    box = np.int0(box)
                    angle = 0
                    width_obj = rect[1][0]
                    height_obj = rect[1][1]
                    min_size = min(width_obj, height_obj)
                    center = rect[0]
                    angle = rect[2]

                    if width_obj < height_obj:
                        angle = 90 - rect[2]
                    else:
                        angle = -rect[2]

                    angle = -angle 
                    
                    #Desenez orientarea robotului
                    #(rect_x, rect_y), (width_obj, height_obj), angle = rect                    
                    start_point_orientation = (int(item[0] + item[2] * 0.5), int(item[1] + item[3] * 0.5))
                    #self.frame = cv2.line(self.frame, start_point_orientation, (box[0][0] + box[1][0] + box[2][0] + box[3][0], box[0][1] + box[1][1] + box[2][1] + box[3][1]), (0,255,255), 5)

                    end_point_orientation_north = (int(item[0] + item[2] * 0.5) , abs(int(item[1] + item[3] * 0.5) - int(min_size * 0.75)))
                    end_point_orientation_south = (int(item[0] + item[2] * 0.5) , abs(int(item[1] + item[3] * 0.5) + int(min_size * 0.75)))
                    
                    x_p_north = end_point_orientation_north[0] - start_point_orientation[0]
                    x_p_south = end_point_orientation_south[0] - start_point_orientation[0]

                    y_p_north = end_point_orientation_north[1] - start_point_orientation[1]
                    y_p_south = end_point_orientation_south[1] - start_point_orientation[1]

                    x_rotation_north = np.cos(np.radians(angle))*x_p_north - np.sin(np.radians(angle))*y_p_north
                    x_rotation_south = np.cos(np.radians(angle))*x_p_south - np.sin(np.radians(angle))*y_p_south

                    y_rotation_north = np.sin(np.radians(angle))*x_p_north + np.cos(np.radians(angle))*y_p_north
                    y_rotation_south = np.sin(np.radians(angle))*x_p_south + np.cos(np.radians(angle))*y_p_south

                    end_point_orientation_north = (int(start_point_orientation[0]+x_rotation_north), int(start_point_orientation[1]+y_rotation_north))
                    end_point_orientation_south = (int(start_point_orientation[0]+x_rotation_south), int(start_point_orientation[1]+y_rotation_south))


                    #self.frame = cv2.line(self.frame, start_point_orientation, end_point_orientation_north, (0,255,0), 2)
                    #self.frame = cv2.line(self.frame, start_point_orientation, end_point_orientation_east, (0,255,0), 2)
                    #self.frame = cv2.line(self.frame, start_point_orientation, end_point_orientation_south, (0,255,0), 2)
                    #self.frame = cv2.line(self.frame, start_point_orientation, end_point_orientation_west, (0,255,0), 2)
                    
                    #print(end_point_orientation_north, end_point_orientation_south)
                    
                    north_color = tmp_frame[end_point_orientation_north[1] % self.config.config["imgHeight"],end_point_orientation_north[0] % self.config.config["imgWidth"]]
                    south_color = tmp_frame[end_point_orientation_south[1] % self.config.config["imgHeight"],end_point_orientation_south[0] % self.config.config["imgWidth"]]
                    center_color = tmp_frame[start_point_orientation[1] % self.config.config["imgHeight"],start_point_orientation[0] % self.config.config["imgWidth"]]

                    north_color = (int(north_color[0]), int(north_color[1]), int(north_color[2]))
                    south_color = (int(south_color[0]), int(south_color[1]), int(south_color[2]))
                    center_color = (int(center_color[0]), int(center_color[1]), int(center_color[2]))

                    robot_role_color = (255, 255, 255)
                    robot_direction = start_point_orientation

                   

                    if north_color[0] >= self.config.config["teamStrikerRGBMin"][2] and north_color[0] <= self.config.config["teamStrikerRGBMax"][2] and \
                       north_color[1] >= self.config.config["teamStrikerRGBMin"][1] and north_color[1] <= self.config.config["teamStrikerRGBMax"][1] and \
                       north_color[2] >= self.config.config["teamStrikerRGBMin"][0] and north_color[2] <= self.config.config["teamStrikerRGBMax"][0]:
                        robot_role_color = north_color
                        robot_direction = end_point_orientation_north
                        
                    elif south_color[0] >= self.config.config["teamStrikerRGBMin"][2] and south_color[0] <= self.config.config["teamStrikerRGBMax"][2] and \
                       south_color[1] >= self.config.config["teamStrikerRGBMin"][1] and south_color[1] <= self.config.config["teamStrikerRGBMax"][1] and \
                       south_color[2] >= self.config.config["teamStrikerRGBMin"][0] and south_color[2] <= self.config.config["teamStrikerRGBMax"][0]:
                        robot_role_color = south_color
                        robot_direction = end_point_orientation_south

                    elif north_color[0] >= self.config.config["teamKeeperRGBMin"][2] and north_color[0] <= self.config.config["teamKeeperRGBMax"][2] and \
                       north_color[1] >= self.config.config["teamKeeperRGBMin"][1] and north_color[1] <= self.config.config["teamKeeperRGBMax"][1] and \
                       north_color[2] >= self.config.config["teamKeeperRGBMin"][0] and north_color[2] <= self.config.config["teamKeeperRGBMax"][0]:
                        robot_role_color = north_color
                        robot_direction = end_point_orientation_north
                        
                    elif south_color[0] >= self.config.config["teamKeeperRGBMin"][2] and south_color[0] <= self.config.config["teamKeeperRGBMax"][2] and \
                       south_color[1] >= self.config.config["teamKeeperRGBMin"][1] and south_color[1] <= self.config.config["teamKeeperRGBMax"][1] and \
                       south_color[2] >= self.config.config["teamKeeperRGBMin"][0] and south_color[2] <= self.config.config["teamKeeperRGBMax"][0]:
                        robot_role_color = south_color
                        robot_direction = end_point_orientation_south

                    frame = cv2.line(frame, start_point_orientation, robot_direction, robot_role_color, 5)
                        
                    
                   # self.frame = cv2.rectangle(self.frame, start, end, (self.config.config["boundRGBMin"][2],
                  #      self.config.config["boundRGBMin"][1], self.config.config["boundRGBMin"][0]), 2)

                #flag = self.thread_running 

                if self.config.config["windowMode"] == "advanced":
        
                    my_frame = cv2.resize(frame, (self.config.config["displayImgWidth"], self.config.config["displayImgHeight"]))
                    gui_frame = cv2.resize(self.gui_frame, (self.config.config["displayImgWidth"], self.config.config["displayImgHeight"]))

                    self.ui.update(gui_frame)
                    self.ui.gui(gui_frame)
                    self.ui.update_context()
                    
                    output_frame = np.hstack((my_frame, gui_frame))
                    cv2.line(output_frame, (self.config.config["displayImgWidth"] - 1, 0),
                            (self.config.config["displayImgWidth"] - 1, self.config.config["displayImgHeight"] * 2), (100, 22, 150), 2)
                else: 
                    my_frame = cv2.resize(frame, (self.config.config["displayImgWidth"], self.config.config["displayImgHeight"]))
                    color_frame = cv2.resize(draw_color_frame, (self.config.config["displayImgWidth"], self.config.config["displayImgHeight"]))
                    edges = cv2.resize(self.edges, (self.config.config["displayImgWidth"], self.config.config["displayImgHeight"]))
                    gui_frame = cv2.resize(self.gui_frame, (self.config.config["displayImgWidth"], self.config.config["displayImgHeight"]))

                    self.ui.update(gui_frame)
                    self.ui.gui(gui_frame)
                    self.ui.update_context()
                    
                    tmp_first_row_frame = np.hstack((gui_frame, my_frame)) #Combina cele 2 fereste intr-una mai lunguiata, pe orizontal
                    tmp_second_row_frame = np.hstack((color_frame, edges))
                    cv2.line(tmp_second_row_frame, (0, 0),
                            (self.config.config["displayImgWidth"] * 2, 0), (100, 22, 150), 2)
                    output_frame = np.vstack((tmp_first_row_frame, tmp_second_row_frame))
                    cv2.line(output_frame, (self.config.config["displayImgWidth"] - 1, 0),
                            (self.config.config["displayImgWidth"] - 1, self.config.config["displayImgHeight"] * 2), (100, 22, 150), 2)


                cv2.imshow(self.name, output_frame)
        

    def close_device(self, window = True):  #functia close_device inchide camera si/sau fereastra(window-ul)
        self.running = False
        self.thread_running = True

        if self.cam != None:
            self.cam.release() #inchide camera

        if window == True:  #window e un parametru, si doar cand e True, inchid cu adevarat camera, fiind parametru al functiei in def close_device(self, -> window = True <- ):
            cv2.destroyAllWindows() #aici distruge(inchide) toate ferestrele pe care programul le-a deschis pentru a rula programul
            #cv2.destroyWindow(self.name)
            self.window_created = False #asta-i flag pentru fereastra creeata

    def clear(self):
        print("\t\t-clearing WEBCAM data from memory...")
        self.close_device()
