import webcam
import globals
import threading
import time
import configs
import singleton
import log

print("Program is starting soon... (wait for the '>>' sign)")
global_data = globals.Globals()
config = configs.Configs()
config.config["RGBMin"] = config.config["teamOneRGBMin"]
config.config["RGBMax"] = config.config["teamOneRGBMax"]
logger = log.Logger()

cam = None
running = True
restart_cam = False
restart_flag = False

def camera():
    cam.init() #initializeaza camera
    cam.capture() #captureaza fiecare frame, afisand ceea ce vede camera
    cam.close_device(restart_flag) #Inchide window-ul si camera daca flag-ul "restart_flag" este TRUE

def main():
    global running
    global restart_cam
    global restart_flag
    
    while running:
        command = input(">> ")

        command.strip()
        msg_data = command.split()

        if len(msg_data) == 1:
            if msg_data[0] in ("stop", "exit", "close"):
                if cam != None:
                    cam.thread_running = False
                else:
                    print("Camera is not ready!")
                running = False

            if msg_data[0] in ("h", "help"):
                print("\nProgram commands: \n\t (stop, exit, close) -> to terminate the program --- Example: 'stop'" +
                                          "\n\t (conf, config, configs, configuration) + (on/off, start/exit, boot/stop/shutdown/close, enable/disable) -> toggle config runtime read script" +
                      "\n\nWebcam commands: \n\t(re, restart, retry, reboot) + (cam, " +
                      "camera, web, webcam) -> to restart the webcam --- Example: 're cam'" +
                      "\n\t(re, restart, retry, reboot) + (dev, device, win, window) -> " +
                      "to restart the window and the webcam --- Example: 're dev'" +
                      "\n\nTeam commands: \n\t(bind) + (team) + (first/second, one/two, 1/2) ->" +
                      "binds the rgb min and max of the selected team for the color recognition software --- Example: 'bind team 1'\n")
                
        elif len(msg_data) == 2:
            if msg_data[0] in ["re", "restart", "retry", "reboot"]:
                if msg_data[1] in ["cam", "camera", "web", "webcam"]:
                    print("\nRestarting the camera device...\n")
                    restart_cam = True
                    
                    if cam != None:
                        cam.thread_running = False
                    else:
                        print("Camera is not ready!")
                elif msg_data[1] in ["dev", "device", "win", "window"]:
                    print("\nRestarting the window and camera device...\n")
                    restart_flag = True
                    restart_cam = True
                    
                    if cam != None:
                        cam.thread_running = False
                    else:
                        print("Camera is not ready!")

            if msg_data[0] in ["conf", "config", "configs", "configuration"]:
                if msg_data[1] in ["on", "start", "boot", "enable"]:
                    print("\nEnabling the runtime config file read script (the config file input gets updated each second)!")
                    config.config_runtime_thread = True
                    config.config["toggleConfigRuntimeRead"] = "on"
                elif msg_data[1] in ["off", "exit", "stop", "shutdown", "close", "disable"]:
                    print("\nDisabling the runtime config file read script!")
                    config.config_runtime_thread = False
                    config.config["toggleConfigRuntimeRead"] = "off"

        elif len(msg_data) == 3:
            if msg_data[0] in ["bind"]:
                if msg_data[1] in ["team"]:
                    if msg_data[2] in ["first", "one", "1"]:
                        print("\nBinding team one color configs...")
                        global_data.bound_team = 1
                        config.config["RGBMin"] = config.config["teamOneRGBMin"]
                        config.config["RGBMax"] = config.config["teamOneRGBMax"]
                    elif msg_data[2] in ["second", "two", "2"]:
                        print("\nBinding team two color configs...")
                        global_data.bound_team = 2
                        config.config["RGBMin"] = config.config["teamTwoRGBMin"]
                        config.config["RGBMax"] = config.config["teamTwoRGBMax"]

cam = webcam.WebcamCapture(global_data.window_name)

# Command prompt input thread // Cand am un command prompt am nev de un while
# Thread-ul acesta are rolul de a citi de la tastatura comenzile (PS, nu trebuie oprit decat la iesirea completa din program)
camera_thread = threading.Thread(target = main, args=())
camera_thread.daemon = True
camera_thread.start()

# Read config file at runtime thread // Citeste si scrie din/in configs.txt (scrie ceea ce modific in UI)
config_thread = threading.Thread(target = config.read_config_runtime, args=(global_data.config_path,))
config_thread.daemon = True
config_thread.start()


draw_thread = threading.Thread(target = cam.draw_frame, args=())
draw_thread.daemon = True
draw_thread.start()

while True: #Thread-ul principal -> Aici ruleaza programul principal. Se ocupa de preluarea imaginii de la webcam + depistarea culorii
    restart_flag = False
    re = False
    cam.thread_running = True
    camera() #Un constructor de la

    if restart_cam == False or \
        global_data.program_running == False:
        break        

running = False
global_data.program_running = False
config.config_runtime_thread = False
cam.thread_running = False

config.update_config(global_data.config_path + ".txt")

print("\nClosing the program...")
print("\tClearing the memory:\n")
cam.clear()
logger.clear()
config.clear()
