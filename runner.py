from enum import Enum
import os
from subprocess import Popen
import configparser

class ModeException(Exception):
    pass

class CopterMode(Enum):
    SIMULATED = 1
    REAL = 2

'''
    This Runner expects ardupilot to be installed in ~/gradys/ardupilot.
    To change ardupilot installation path call the method setArdupilot(ardupilot_path)
'''
class Runner:

    def __init__(self, mode):
        # Copter Mode
        if self.__setMode(mode) == False:
            raise ModeException("Invalid Mode")

        # Simulation Params
        self.__sysid = None
        self.__location = None

        # General Params
        self.__api_port = None
        self.__connection = None
    
        # Internal Process
        self.__api_process = None
        self.__sitl_process = None

        # ConfigParser
        self.__config = None

        # Ardupilot Path
        self.__ardupilot = "~/gradys/ardupilot"
    @staticmethod
    def __print(text):
        print("[Runner] " + text)

    def __startSITL(self):
        sitl_command = f'xterm -e {self.__ardupilot}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {self.__sysid} --sysid {self.__sysid} -N -L {self.__location} --out {self.__connection}'
        sitl_command = sitl_command.split(" ")

        self.__sitl_process = Popen(sitl_command)

    def __runAPI(self):
        api_command = "fastapi dev uav_api.py"
        api_command = api_command.split(" ")

        env = os.environ.copy()
        env["CONNECTION_STRING"] = self.connection
        self.__api_process = Popen(api_command, env=env)

    def __setMode(self, mode):
        if mode != CopterMode.SIMULATED and mode != CopterMode.REAL:
            self.__print("Invalid mode! (mode=%d)" % mode)
            return False
        self.__mode = mode
        self.__print("New mode! (mode=%s)" % mode.name)
        return True
    
    def __exit(self):
        if self.__sitl_process != None:
            self.__sitl_process.terminate()
        if self.__api_process != None:
            self.__api_process.terminate()

    def setParams(self, sysid=None, connection=None, api_port=None, location=None):
        self.__sysid = sysid if sysid != None else self.__sysid
        self.__connection = connection if connection != None else self.__connection
        self.__api_port = api_port if api_port != None else self.__api_port
        self.__location = location if location != None else self.__location

    def setParamsFromConfig(self, file_path):
        self.__config = configparser.ConfigParser()
        self.__config.read(file_path)

        if self.__mode == CopterMode.SIMULATED:
            self.__sysid = self.__config["SIMULATION PARAMS"]["sysid"]
            self.__location = self.__config["SIMULATION PARAMS"]["loc"]
        
        self.__connection = self.__config["GENERAL PARAMS"]["connection"]
        self.__api_port = self.__config["GENERAL PARAMS"]["api-port"]

    def setArdupilot(self, path):
        self.__ardupilot = path

    def run(self):
        # Verifying mode value
        if self.__mode == None:
            self.__print("Mode not defined!")
            return
        
        # Run SITL if necessary
        if self.__mode == CopterMode.SIMULATED:
            self.__startSITL()
        
        self.__runAPI()

        cmd = ""
        while cmd != "exit":
            cmd = input("Digite um comando: ")
        
        self.__exit()
