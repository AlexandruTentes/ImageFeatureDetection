from datetime import datetime
import inspect
import time
import singleton
import math

class Utility(metaclass=singleton.Singleton):    
    new_fps = 0
    prev_fps = 0
    time_elapsed = 0
    frame_count = 0
    
    def __init__(self):
        pass

    def get_time(self):
        time = datetime.now()
        current_time = time.strftime("%d/%m/%Y, %H:%M:%S")
        time_arr = current_time.split(',')
        current_time_day = time_arr[0].strip()
        current_time_hour = time_arr[1].strip()
        return (current_time_day, current_time_hour)

    def get_codeline(self):
        current_info = inspect.currentframe()
        frame_info = inspect.getouterframes(current_info, 2)
        return (frame_info[2][1], frame_info[2][2])

    def dist2D(self, one, two):
        dx = one[0] - two[0];
        dy = one[1] - two[1];
        return math.sqrt(dx*dx + dy*dy);

    def angle3P(self, p1, p2, p3):
        a = self.dist2D(p3, p1);
        b = self.dist2D(p3, p2);
        c = self.dist2D(p1, p2);

        numer = c**2 - a**2 - b**2;
        denom = -2 * a * b;
        if denom == 0:
            denom = 0.000001;
        rads = math.acos(numer / denom);
        degs = math.degrees(rads);

        return degs;

    def translateRotation(self, rotation, width, height):
        if (width < height):
            rotation = -1 * (rotation - 90)
        if (rotation > 90):
            rotation = -1 * (rotation - 180)
        rotation *= -1
        return round(rotation)
    
    def fps_counter(self, flag = False):
        if flag == False:
            self.new_fps = time.time()
            fps = 1 / (self.new_fps - self.prev_fps)
            self.prev_fps = self.new_fps
            return str(int(fps)) 
        else:
            self.frame_count = self.frame_count + 1

            if self.time_elapsed == 0:
                self.time_elapsed = time.time()
                return str(self.frame_count)

            time_diff = time.time() - self.time_elapsed

            if time_diff >= 1:
                self.time_elapsed = time.time()
                result = str(int(self.frame_count / time_diff))
                self.frame_count = 0
                return result

            return ""

    def string_to_number(self, string):
        if string == "":
            return 0

        tmp_string = (string + ".")[:-1]
        
        if string[0] in ('-', '+'):
            tmp_string = string[1:]
        
        if tmp_string.replace('.','',1).isdigit():
            if len(tmp_string.split('.')) == 1:
                return int(string)
            else:
                return float(string)

        return string
