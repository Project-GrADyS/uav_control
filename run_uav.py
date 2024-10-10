import os
from argparse import ArgumentParser
import configparser
from subprocess import Popen
from protocol.provider import UavControlProvider
from protocol.test import TestProtocol
import requests
from time import sleep

parser = ArgumentParser()

parser.add_argument(
    '--protocol',
    dest='protocol',
    default=False,
    help="If run_uav should run a protocol"
)

parser.add_argument(
    '--simulated',
    dest='simulated',
    default=False,
    help="If run_uav is simulated"
)

parser.add_argument(
    '--config',
    dest='config',
    default='/etc/uav_config.ini',
    help="Config file to extract configurations from"
)

parser.add_argument(
    '--uav_sysid',
    dest='uav_sysid',
    type=int,
    default=10,
    help="Value for uav SYSID to connect through mavlink",  
)

parser.add_argument(
    '--uav_connection',
    dest='connection',
    default='127.0.0.1:17171',
    help="Address for uav connection",  
)

parser.add_argument(
    '--connection_type',
    dest='connection_type',
    default='udpin',
    help="Connection type for Copter connection"
)

parser.add_argument(
    '--uav_api_port',
    dest='uav_api_port',
    default=8000,
    help="Port for uav's FastApi to run"
)

# simulated argument
parser.add_argument(
    '--location',
    dest='location',
    default=["AbraDF"],
    help="Location name for copters. The number os locations passed must be equal to 'n' argument. Location order is relevant.",
    nargs='*'
)

#simulated argument
parser.add_argument(
    '--gs_connection',
    dest='gs_connection',
    default=["172.26.176.1:15630", "172.31.16.1:15630"],
    help="Address for GroundStation connection",
    nargs='*'
)

#simulated argument
parser.add_argument(
    '--ardupilot_path',
    dest='ardupilot_path',
    default='~/gradys/ardupilot',
    help="Path for ardupilot repository"
)

#simulated argument
parser.add_argument(
    '--n',
    dest='n',
    default=1,
    type=int,
    help="Number of simulated UAVs"
)

#simulated argument
parser.add_argument(
    '--speedup',
    dest='speedup',
    default=1,
    help="Speed of the simulation"
)

args = parser.parse_args()
uav_args = {}

uav_args["sysid"] = args.uav_sysid
uav_args["uav_connection"] = args.connection
uav_args["connection_type"] = args.connection_type
uav_args["location"] = args.location
uav_args["gs_connection"] = args.gs_connection
uav_args["api_port"] = args.uav_api_port
uav_args["ardupilot_path"] = args.ardupilot_path
uav_args["speedup"] = args.speedup
uav_args["n"] = args.n
# gets config if is real-flight or if config argument was passed in simulated mode
if args.simulated == False or args.config != "/etc/uav_config.ini": 
    # getting configs from /etc
    config = configparser.ConfigParser()
    config.read(args.config)
    if not "GENERAL" in config:
        raise Exception("Missing GENERAL key in uav config file (.ini)")
    uav_args["sysid"] = int(config["GENERAL"]["sysid"])
    uav_args["uav_connection"] = config["GENERAL"]["uav_connection"]
    uav_args["connection_type"] = config["GENERAL"]["connection_type"]
    uav_args["api_port"] = config["GENERAL"]["api_port"]
    if args.simulated:
        if not "SIMULATED" in config:
            raise Exception("Missing SIMULATED in config file while in simulated mode")
        uav_args["ardupilot_path"] = config["SIMULATED"]["ardupilot_path"] if "ardupilot_path" in config["SIMULATED"] else uav_args["ardupilot_path"]
        uav_args["location"] = config["SIMULATED"]["location"].strip("[]").split(", ") if "location" in config["SIMULATED"] else uav_args["location"]
        uav_args["gs_connection"] = config["SIMULATED"]["gs_connection"].strip("[]").split(", ") if "gs_connection" in config["SIMULATED"] else uav_args["gs_connection"]
        uav_args["n"] = int(config["SIMULATED"]["n"]) if "n" in config["SIMULATED"] else uav_args["n"]
        uav_args["speedup"] = config["SIMULATED"]["speedup"] if "speedup" in config["SIMULATED"] else uav_args["speedup"]

print(uav_args)
api_process = []

if args.simulated:
    # starting SITL
    for i in range(uav_args["n"]):
        host, port = uav_args["uav_connection"].split(":")
        uav_connection = f"{host}:{str(int(port) + i)}"
        sitl_command = f"xterm -e {uav_args['ardupilot_path']}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {uav_args['sysid']+i} --sysid {uav_args['sysid']+i} -N -L {uav_args['location'][i]} --speedup {uav_args['speedup']} --out {uav_connection} {' '.join([f'--out {address}' for address in uav_args['gs_connection']])} &"
        api_command = f"python3 uav_api.py --sysid {uav_args['sysid']+i} --uav_connection {uav_connection} --connection_type {uav_args['connection_type']} --port {str(int(uav_args['api_port'])+i)}".split(" ")
        os.system(sitl_command)
        api_process.append(Popen(api_command))
        #os.system(api_command)
else:
    api_command = f"python3 uav_api.py --sysid {uav_args['sysid']} --uav_connection {uav_args['uav_connection']} --connection_type {uav_args['connection_type']} --port {str(uav_args['api_port'])}"
    os.system(api_command)

if args.protocol:
    api_url = f"http://localhost:{uav_args['api_port']}"

    # Wait for SITL and FastAPI start
    sleep(5)

    # Arming vehicle
    result = requests.get(f"{api_url}/command/arm")
    if result.status_code != 200:
        terminate()
        raise Exception("Vehicle not armed")

    result = requests.get(f"{api_url}/command/takeoff", params={"alt": 15})
    if result.status_code != 200:
        terminate()
        raise Exception("Vehicle takeoff fail")
    provider = UavControlProvider(uav_args["sysid"], api_url)
    protocol = TestProtocol.instantiate(provider)

    protocol.initialize()
        
cmd = ""
while cmd != "stop":
    cmd = input("Digite um comando")

def terminate():
    for process in api_process:
        process.terminate()