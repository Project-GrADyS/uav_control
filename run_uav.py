import os
from argparse import ArgumentParser
import configparser
from subprocess import Popen
parser = ArgumentParser()

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
    '--uav_api_port',
    dest='uav_api_port',
    default=8000,
    help="Port for uav's FastApi to run"
)

# simulated argument
parser.add_argument(
    '--uav_location',
    dest='location',
    default="AbraDF",
    help="Value for uav HOME LOCATION"
)

#simulated argument
parser.add_argument(
    '--gs_connection',
    dest='gs_connection',
    default=["172.26.176.1:15630"],
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
    help="Number of simulated UAVs"
)

args = parser.parse_args()
print(args)
print(args.uav_sysid)
uav_args = {}

# gets config if is real-flight or if config argument was passed in simulated mode
if args.simulated == False or args.config != "/etc/uav_config.ini": 
    # getting configs from /etc
    config = configparser.ConfigParser()
    config = config.read(args.config)

    if not "GENERAL" in config:
        raise Exception("Missing GENERAL key in uav config file (.ini)")
    uav_args["sysid"] = config["GENERAL"]["sysid"]
    uav_args["uav_connection"] = config["GENERAL"]["uav_connection"]
    uav_args["api_port"] = config["GENERAL"]["api_port"]
    if args.simulated == True:
        if not "SIMULATED" in config:
            raise Exception("Missing SIMULATED in config file while in simulated mode")
        uav_args["ardupilot_path"] = config["SIMULATED"]["ardupilot_path"] if "ardupilot_path" in config["SIMULATED"] else args.ardupilot_path
        uav_args["location"] = config["SIMULATED"]["location"] if "location" in config["SIMULATED"] else args.uav_location
        uav_args["gs_connection"] = config["SIMULATED"]["gs_connection"] if "gs_connection" in config["SIMULATED"] else args.gs_connection
        uav_args["n"] = config["SIMULATED"]["n"] if "n" in config["SIMULATED"] else args.n
else:
    uav_args["sysid"] = args.uav_sysid
    uav_args["uav_connection"] = args.connection
    uav_args["location"] = args.location
    uav_args["gs_connection"] = args.gs_connection
    uav_args["api_port"] = args.uav_api_port
    uav_args["ardupilot_path"] = args.ardupilot_path

api_process = []

if args.simulated:
    # starting SITL
    for i in range(int(args.n)):
        host, port = uav_args["uav_connection"].split(":")
        uav_connection = f"{host}:{str(int(port) + i)}"
        sitl_command = f"xterm -e {uav_args['ardupilot_path']}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {uav_args['sysid']+i} --sysid {uav_args['sysid']+i} -N -L {uav_args['location']} --out {uav_connection} {' '.join([f'--out {address}' for address in uav_args['gs_connection']])} &"
        api_command = f"python3 uav_api.py --sysid {uav_args['sysid']+i} --uav_connection {uav_connection} --port {int(uav_args['api_port'])+i}".split(" ")
        os.system(sitl_command)
        api_process.append(Popen(api_command))
else:
    api_command = f"python3 uav_api.py --sysid {uav_args['sysid']} --uav_connection {uav_args['uav_connection']}' --port {uav_args['api_port']}"
    os.system(api_command)
cmd = ""
while cmd != "exit":
    cmd = input("Digite um comando")
for process in api_process:
    process.terminate()