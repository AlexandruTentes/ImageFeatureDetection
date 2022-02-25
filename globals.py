import singleton

class Globals(metaclass=singleton.Singleton):    
    log_path = "logs\\Log"
    window_name = "Licence"
    config_path = "Configs"
    program_running = True
    bound_team = 1
