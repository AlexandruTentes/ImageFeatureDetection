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

    ball_color_R_min_value = None
    ball_color_G_min_value = None
    ball_color_B_min_value = None
    ball_color_R_max_value = None
    ball_color_G_max_value = None
    ball_color_B_max_value = None
    
    display_frame_text = "OFF"
    
    def __init__(self):
        self.global_data = globals.Globals()
        self.config = configs.Configs()

        self.image_frame_width_value = [self.config.config["displayImgWidth"]]
        self.image_frame_height_value = [self.config.config["displayImgHeight"]]

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

        self.ball_color_R_min_value = [self.config.config["ballRGBMin"][0]]
        self.ball_color_G_min_value = [self.config.config["ballRGBMin"][1]]
        self.ball_color_B_min_value = [self.config.config["ballRGBMin"][2]]
        self.ball_color_R_max_value = [self.config.config["ballRGBMax"][0]]
        self.ball_color_G_max_value = [self.config.config["ballRGBMax"][1]]
        self.ball_color_B_max_value = [self.config.config["ballRGBMax"][2]]

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

        r = 1.77
        ratio_x = self.config.config["displayImgWidth"] / 1920 * r
        ratio_y = self.config.config["displayImgHeight"] / 1080 * r
        ratio = (ratio_x + ratio_y) / r
        cvui.text(frame, 100*ratio_x, 25*ratio_y, 'Configuration:')

        #displayFrameText
        cvui.text(frame, 100*ratio_x, 82.5*ratio_y, 'Display Frame Text')

        if cvui.button(frame, 300*ratio_x, 75*ratio_y, self.display_frame_text):
            if self.display_frame_text == "OFF":
                self.config.config["displayFrameText"] = "on"
                self.display_frame_text = "ON"
            else:
                self.config.config["displayFrameText"] = "off"
                self.display_frame_text = "OFF"

        #boundTeam
        if cvui.button(frame, 600*ratio_x, 75*ratio_y, "Bound team: " + self.bound_team_text):
            if self.bound_team_text == "1":
                self.global_data.bound_team = 2
                self.bound_team_text = "2"
            else:
                self.global_data.bound_team = 1
                self.bound_team_text = "1"

        #displayImgWidth
        cvui.text(frame, 100*ratio_x, 140*ratio_y, 'Image Frame Width')
        cvui.trackbar(frame, 300*ratio_x, 125*ratio_y, 200*ratio, self.image_frame_width_value, 640, 960)
        self.config.config["displayImgWidth"] = int(self.image_frame_width_value[0])

        #displayImgHeight
        cvui.text(frame, 100*ratio_x, 190*ratio_y, 'Image Frame Height')
        cvui.trackbar(frame, 300*ratio_x, 175*ratio_y, 200*ratio, self.image_frame_height_value, 360, 540)
        self.config.config["displayImgHeight"] = int(self.image_frame_height_value[0])

        #TEAM UI

        #TEAM 1
        #teamOneRGBMin
        cvui.text(frame, 100*ratio_x, 230*ratio_y, 'First team color')
        cvui.trackbar(frame, 300*ratio_x, 225*ratio_y, 100*ratio, self.first_team_color_R_min_value, 0, 255)
        cvui.trackbar(frame, 450*ratio_x, 225*ratio_y, 100*ratio, self.first_team_color_G_min_value, 0, 255)
        cvui.trackbar(frame, 600*ratio_x, 225*ratio_y, 100*ratio, self.first_team_color_B_min_value, 0, 255)
        cvui.text(frame, 700*ratio_x, 245*ratio_y, 'MIN')
        self.config.config["teamOneRGBMin"] = [
            int(self.first_team_color_R_min_value[0]),
            int(self.first_team_color_G_min_value[0]),
            int(self.first_team_color_B_min_value[0])
        ]

        #teamOneRGBMax
        cvui.trackbar(frame, 300*ratio_x, 275*ratio_y, 100*ratio, self.first_team_color_R_max_value, 0, 255)
        cvui.trackbar(frame, 450*ratio_x, 275*ratio_y, 100*ratio, self.first_team_color_G_max_value, 0, 255)
        cvui.trackbar(frame, 600*ratio_x, 275*ratio_y, 100*ratio, self.first_team_color_B_max_value, 0, 255)
        cvui.text(frame, 700*ratio_x, 295*ratio_y, 'MAX')
        self.config.config["teamOneRGBMax"] = [
            int(self.first_team_color_R_max_value[0]),
            int(self.first_team_color_G_max_value[0]),
            int(self.first_team_color_B_max_value[0])
        ]

        #TEAM 2
        #teamTwoRGBMin
        cvui.text(frame, 100*ratio_x, 340*ratio_y, 'Second team color')
        cvui.trackbar(frame, 300*ratio_x, 325*ratio_y, 100*ratio, self.second_team_color_R_min_value, 0, 255)
        cvui.trackbar(frame, 450*ratio_x, 325*ratio_y, 100*ratio, self.second_team_color_G_min_value, 0, 255)
        cvui.trackbar(frame, 600*ratio_x, 325*ratio_y, 100*ratio, self.second_team_color_B_min_value, 0, 255)
        cvui.text(frame, 700*ratio_x, 345*ratio_y, 'MIN')
        self.config.config["teamTwoRGBMin"] = [
            int(self.second_team_color_R_min_value[0]),
            int(self.second_team_color_G_min_value[0]),
            int(self.second_team_color_B_min_value[0])
        ]

        #teamTwoRGBMax
        cvui.trackbar(frame, 300*ratio_x, 375*ratio_y, 100*ratio, self.second_team_color_R_max_value, 0, 255)
        cvui.trackbar(frame, 450*ratio_x, 375*ratio_y, 100*ratio, self.second_team_color_G_max_value, 0, 255)
        cvui.trackbar(frame, 600*ratio_x, 375*ratio_y, 100*ratio, self.second_team_color_B_max_value, 0, 255)
        cvui.text(frame, 700*ratio_x, 395*ratio_y, 'MAX')
        self.config.config["teamTwoRGBMax"] = [
            int(self.second_team_color_R_max_value[0]),
            int(self.second_team_color_G_max_value[0]),
            int(self.second_team_color_B_max_value[0])
        ]

        #BALL
        #ballRGBMin
        cvui.text(frame, 100*ratio_x, 440*ratio_y, 'Ball Color')
        cvui.trackbar(frame, 300*ratio_x, 425*ratio_y, 100*ratio, self.ball_color_R_min_value, 0, 255)
        cvui.trackbar(frame, 450*ratio_x, 425*ratio_y, 100*ratio, self.ball_color_G_min_value, 0, 255)
        cvui.trackbar(frame, 600*ratio_x, 425*ratio_y, 100*ratio, self.ball_color_B_min_value, 0, 255)
        cvui.text(frame, 700*ratio_x, 445*ratio_y, 'MIN')
        self.config.config["ballRGBMin"] = [
            int(self.ball_color_R_min_value[0]),
            int(self.ball_color_G_min_value[0]),
            int(self.ball_color_B_min_value[0])
        ]

        #ballRGBMax
        cvui.trackbar(frame, 300*ratio_x, 475*ratio_y, 100*ratio, self.ball_color_R_max_value, 0, 255)
        cvui.trackbar(frame, 450*ratio_x, 475*ratio_y, 100*ratio, self.ball_color_G_max_value, 0, 255)
        cvui.trackbar(frame, 600*ratio_x, 475*ratio_y, 100*ratio, self.ball_color_B_max_value, 0, 255)
        cvui.text(frame, 700*ratio_x, 495*ratio_y, 'MAX')
        self.config.config["ballRGBMax"] = [
            int(self.ball_color_R_max_value[0]),
            int(self.ball_color_G_max_value[0]),
            int(self.ball_color_B_max_value[0])
        ]

        self.config.update_static_configs()

    def update_context(self):
        cvui.update()
