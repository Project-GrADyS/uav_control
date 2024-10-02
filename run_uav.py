import os
from argparse import ArgumentParser
from runner import Runner, CopterMode
import configparser
parser = ArgumentParser()

parser.add_argument(
    '--simulated',
    dest='simulated',
    default=None,
    help="If run_uav is simulated"
)

# simulated argument
parser.add_argument(
    '--config',
    dest='config',
    default=None,
    help="Config file to extract configurations from"
)

# simulated argument
parser.add_argument(
    '--uav_sysid',
    dest='sysid',
    default=None,
    help="Value for uav SYSID to connect through mavlink",  
)

# simulated argument
parser.add_argument(
    '--uav_connection',
    dest='connection',
    default=None,
    help="Address for uav connection",  
)

# simulated argument
parser.add_argument(
    '--uav_location',
    dest='location',
    default=None,
    help="Value for uav HOME LOCATION"
)

# simulated argument
parser.add_argument(
    '--uav_api_port',
    dest='uav_api_port',
    default=None,
    help="Port for uav's FastApi to run"
)

parser.add_argument(
    '--gs_connection',
    dest='gs_connection',
    default=None,
    help="Address for GroundStation connection"
)

args = parser.parse_args()

uav_args = {}

# REAL FLIGHT
if args.simulated == None:
    # getting configs from /etc
    config_parser = configparser.ConfigParser()
    config = configparser.read("/etc/uav_config.ini")
    uav_args["sysid"] = config["RUNNER"]["sysid"]
    uav_args["uav_connection"] = config["RUNNER"]["uav_connection"]
    uav_args["location"] = config["RUNNER"]["location"]
    uav_args["gs_connection"] = config["RUNNER"]["gs_connection"]
# SIMULATED FLIGHT
else:
    # getting configs from config file
    if args.config != None:
        config_parser = configparser.ConfigParser()
        config = configparser.read("/etc/uav_config.ini")
        uav_args["sysid"] = config["RUNNER"]["sysid"]
        uav_args["uav_connection"] = config["RUNNER"]["uav_connection"]
        uav_args["location"] = config["RUNNER"]["location"]
        uav_args["gs_connection"] = config["RUNNER"]["gs_connection"]
    # setting configs from arguments
    elif args.uav_sysid != None and args.uav_connection != None and args.uav_location != None and args.gs_connection != None:
        uav_args["sysid"] = args.uav_sysid  
        uav_args["uav_connection"] = args.uav_connection
        uav_args["location"] = args.uav_location
        uav_args["gs_connection"] = args.gs_connection
    else:
        raise Exception("Missing arguments for simulated flight")

    # starting SITL
    sitl_command = f'xterm -e {self.__ardupilot}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {self.__sysid} --sysid {self.__sysid} -N -L {self.__location} --out 127.0.0.1:{self.__udp_port} --out 172.31.16.1:{self.__udp_port} --out 172.26.176.1:{self.__udp_port} &'

    self.__sitl_process = os.system(sitl_command)