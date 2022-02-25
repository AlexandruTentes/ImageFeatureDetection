import cv2
import cvui
import numpy as np
import singleton
import configs
import globals

class UI(metaclass=singleton.Singleton):
    global_data = None
    config = None
    
    image_frame_width_value = None
    image_frame_height_value = None

    bound_team_text = None
    
    first_team_color_R_min_value = None
    first_team_color_G_min_value = None
    first_team_color_B_min_value = None
    first_team_color_R_max_value = None
    first_team_color_G_max_value = None
    first_team_color_B_max_value = None

    second_team_color_R_min_value = None
    second_team_color_G_min_value = None
    second_team_color_B_min_value = None
    second_team_color_R_max_value = None
    second_team_color_G_max_value = None
    second_team_color_B_max_value = None
    
    display_frame_text = "OFF"
    
    def __init__(self):
        self.global_data = globals.Globals()
        self.config = configs.Configs()

        self.image_frame_width_value = [self.config.config["imgWidth"]]
        self.image_frame_height_value = [self.config.config["imgHeight"]]

        self.bound_team_text = str(self.global_data.bound_team)
        
        self.first_team_color_R_min_value = [self.config.config["teamOneRGBMin"][0]]
        self.first_team_color_G_min_value = [self.config.config["teamOneRGBMin"][1]]
        self.first_team_color_B_min_value = [self.config.config["teamOneRGBMin"][2]]
        self.first_team_color_R_max_value = [self.config.config["teamOneRGBMax"][0]]
        self.first_team_color_G_max_value = [self.config.config["teamOneRGBMax"][1]]
        self.first_team_color_B_max_value = [self.config.config["teamOneRGBMax"][2]]

        self.second_team_color_R_min_value = [self.config.config["teamTwoRGBMin"][0]]
        self.second_team_color_G_min_value = [self.config.config["teamTwoRGBMin"][1]]
        self.second_team_color_B_min_value = [self.config.config["teamTwoRGBMin"][2]]
        self.second_team_color_R_max_value = [self.config.config["teamTwoRGBMax"][0]]
        self.second_team_color_G_max_value = [self.config.config["teamTwoRGBMax"][1]]
        self.second_team_color_B_max_value = [self.config.config["teamTwoRGBMax"][2]]

        if self.config.config["displayFrameText"] == "on":
            self.display_frame_text = "ON"
        else:
            self.display_frame_text = "OFF"
        
        cvui.init(self.global_data.window_name)

    def update(self, frame):
        frame[:] = (49, 52, 49)

    def gui(self, frame):
        if self.config.config["toggleUI"] == "off":
            return
        
        cvui.text(frame, 100, 25, 'Configuration:')

        #displayFrameText
        cvui.text(frame, 100, 82.5, 'Display Frame Text')

        if cvui.button(frame, 300, 75, self.display_frame_text):
            if self.display_frame_text == "OFF":
                self.config.config["displayFrameText"] = "on"
                self.display_frame_text = "ON"
            else:
                self.config.config["displayFrameText"] = "off"
                self.display_frame_text = "OFF"

        #boundTeam
        if cvui.button(frame, 600, 75, "Bound team: " + self.bound_team_text):
            if self.bound_team_text == "1":
                self.global_data.bound_team = 2
                self.bound_team_text = "2"
            else:
                self.global_data.bound_team = 1
                self.bound_team_text = "1"

        #imgWidth
        cvui.text(frame, 100, 140, 'Image Frame Width')
        cvui.trackbar(frame, 300, 125, 200, self.image_frame_width_value, 640, 2000)
        self.config.config["imgWidth"] = int(self.image_frame_width_value[0])

        #imgHeight
        cvui.text(frame, 100, 190, 'Image Frame Height')
        cvui.trackbar(frame, 300, 175, 200, self.image_frame_height_value, 480, 1500)
        self.config.config["imgHeight"] = int(self.image_frame_height_value[0])

        #TEAM UI

        #TEAM 1
        #teamOneRGBMin
        cvui.text(frame, 100, 230, 'First team color')
        cvui.trackbar(frame, 300, 225, 100, self.first_team_color_R_min_value, 0, 255)
        cvui.trackbar(frame, 450, 225, 100, self.first_team_color_G_min_value, 0, 255)
        cvui.trackbar(frame, 600, 225, 100, self.first_team_color_B_min_value, 0, 255)
        cvui.text(frame, 700, 245, 'MIN')
        self.config.config["teamOneRGBMin"] = [
            int(self.first_team_color_R_min_value[0]),
            int(self.first_team_color_G_min_value[0]),
            int(self.first_team_color_B_min_value[0])
        ]

        #teamOneRGBMax
        cvui.trackbar(frame, 300, 275, 100, self.first_team_color_R_max_value, 0, 255)
        cvui.trackbar(frame, 450, 275, 100, self.first_team_color_G_max_value, 0, 255)
        cvui.trackbar(frame, 600, 275, 100, self.first_team_color_B_max_value, 0, 255)
        cvui.text(frame, 700, 295, 'MAX')
        self.config.config["teamOneRGBMax"] = [
            int(self.first_team_color_R_max_value[0]),
            int(self.first_team_color_G_max_value[0]),
            int(self.first_team_color_B_max_value[0])
        ]

        #TEAM 2
        #teamTwoRGBMin
        cvui.text(frame, 100, 340, 'Second team color')
        cvui.trackbar(frame, 300, 325, 100, self.second_team_color_R_min_value, 0, 255)
        cvui.trackbar(frame, 450, 325, 100, self.second_team_color_G_min_value, 0, 255)
        cvui.trackbar(frame, 600, 325, 100, self.second_team_color_B_min_value, 0, 255)
        cvui.text(frame, 700, 345, 'MIN')
        self.config.config["teamTwoRGBMin"] = [
            int(self.second_team_color_R_min_value[0]),
            int(self.second_team_color_G_min_value[0]),
            int(self.second_team_color_B_min_value[0])
        ]

        #teamTwoRGBMax
        cvui.trackbar(frame, 300, 375, 100, self.second_team_color_R_max_value, 0, 255)
        cvui.trackbar(frame, 450, 375, 100, self.second_team_color_G_max_value, 0, 255)
        cvui.trackbar(frame, 600, 375, 100, self.second_team_color_B_max_value, 0, 255)
        cvui.text(frame, 700, 395, 'MAX')
        self.config.config["teamTwoRGBMax"] = [
            int(self.second_team_color_R_max_value[0]),
            int(self.second_team_color_G_max_value[0]),
            int(self.second_team_color_B_max_value[0])
        ]

        self.config.update_static_configs()

    def update_context(self):
        cvui.update()
