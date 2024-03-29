import cv2
import numpy as np
import singleton
import sys

class ImageRecognition(metaclass=singleton.Singleton):
   
    kernel = np.ones((5,5), np.uint8)

    def __init__(self):
        pass

    def convert_to_multi_channel(self, frame, original):
        img = np.zeros_like(original)
        row, col, channel = original.shape

        for i in range(channel - 1):
            img[:,:,i] = frame

        return img

    def edge_detection(self, frame, threshold_min, threshold_max):
        #mask = cv2.bilateralFilter(frame, 5, 5, 7) 
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(frame,(5,5),0)
        return cv2.Canny(blur, threshold_min, threshold_max)

    def get_image_objects(self, frame, lower_color, upper_color,
                          threshold_min, threshold_max, gaussian_size, gaussian_sigma,
                          obj_min_width, obj_max_width, obj_min_height, obj_max_height):
        item_list = []

        obj_min_width = (obj_min_width >= 0) * obj_min_width
        obj_min_height = (obj_min_height >= 0) * obj_min_height
        obj_max_width = (obj_max_width < 0) * (sys.maxsize - 1) + (obj_max_width >= 0) * obj_max_width
        obj_max_height = (obj_max_height < 0) * (sys.maxsize - 1) + (obj_max_height >= 0) * obj_max_height

        blur = cv2.GaussianBlur(frame, (gaussian_size, gaussian_size), gaussian_sigma) #Masca care imi blureaza imaginea (configs.txt la 
                                                                                        #"Image processing edge detection thresholding dimensions")
        color_frame = self.color_detection(blur, lower_color, upper_color) #Functia asta imi detecteaza inca o imagine (frame) din care a scos culorile
                                                                            #care nu ma intereseaza
        color_frame = cv2.erode(color_frame, self.kernel, iterations=3)
        color_frame = cv2.dilate(color_frame, self.kernel, iterations=3)
        edges = self.edge_detection(color_frame, threshold_min, threshold_max)
        contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #Acest for imi impacheteaza obiectul depistat intr-o cuite, fara sa tina cont de rotatia obiectului
        for item in contours:
            moment = cv2.moments(item)
            x, y, w, h = cv2.boundingRect(item)
            data = [x, y, w, h, item]
            
            if w >= obj_min_width and w <= obj_max_width and \
               h >= obj_min_height and h <= obj_max_height:
                item_list.append(data)

        return (blur, color_frame, self.convert_to_multi_channel(edges, frame), item_list)

    def color_detection(self, frame, lower_color, upper_color):
        lower_color_rgb = [lower_color[2], lower_color[1], lower_color[0]]
        upper_color_rgb = [upper_color[2], upper_color[1], upper_color[0]]
        
        lower = np.array(lower_color_rgb, dtype = "uint8")
        upper = np.array(upper_color_rgb, dtype = "uint8")

        mask = cv2.inRange(frame, lower, upper)
        return cv2.bitwise_and(frame, frame, mask = mask)
