import os
from argparse import ArgumentParser
import configparser
from subprocess import Popen
from protocol.provider import UavControlProvider
from protocol.test import TestProtocol
import requests
from time import sleep
from protocol.messages.telemetry import Telemetry, Position

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

#protocol argument
parser.add_argument(
    '--pos',
    dest='pos',
    default=['[0,0,0]'],
    help="Initial position of the node in protocol frame in the following format '(x,y,z)'",
    nargs='*'
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
uav_args['pos'] = args.pos
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
            raise Exception("Missing SIMULATED in config file (.ini) while in simulated mode")
        uav_args["ardupilot_path"] = config["SIMULATED"]["ardupilot_path"] if "ardupilot_path" in config["SIMULATED"] else uav_args["ardupilot_path"]
        uav_args["location"] = config["SIMULATED"]["location"].strip("[]").split(", ") if "location" in config["SIMULATED"] else uav_args["location"]
        uav_args["gs_connection"] = config["SIMULATED"]["gs_connection"].strip("[]").split(", ") if "gs_connection" in config["SIMULATED"] else uav_args["gs_connection"]
        uav_args["n"] = int(config["SIMULATED"]["n"]) if "n" in config["SIMULATED"] else uav_args["n"]
        uav_args["speedup"] = config["SIMULATED"]["speedup"] if "speedup" in config["SIMULATED"] else uav_args["speedup"]

print(uav_args)

api_process = []
def terminate():
    for process in api_process:
        process.terminate()

protocols = []

# starting uav's
for i in range(uav_args["n"]):
    host, port = uav_args["uav_connection"].split(":")
    uav_connection = f"{host}:{str(int(port) + i)}"
    api_port = str(int(uav_args['api_port']) + i)
    if args.simulated:
        sitl_command = f"xterm -e {uav_args['ardupilot_path']}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {uav_args['sysid']+i} --sysid {uav_args['sysid']+i} -N -L {uav_args['location'][i]} --speedup {uav_args['speedup']} --out {uav_connection} {' '.join([f'--out {address}' for address in uav_args['gs_connection']])} &"
        os.system(sitl_command)
        print(sitl_command)
    api_command = f"python3 uav_api.py --sysid {uav_args['sysid']+i} --uav_connection {uav_connection} --connection_type {uav_args['connection_type']} --port {api_port}"
    api_command = api_command.split(" ")
    api_process.append(Popen(api_command))
    print(api_command)

if args.protocol:
    # Starting Protocol Setup
    print("----------STARTING PROTOCOL SETUP----------")
    for i in range(uav_args["n"]):
        api_port = str(int(uav_args['api_port']) + i)
        api_url = f"http://localhost:{api_port}"
        uav_sysid = uav_args['sysid'] + i
        # Creating Protocol and Provider objects
        provider = UavControlProvider(uav_args["sysid"], api_url)
        protocols.append(TestProtocol.instantiate(provider))

        # Wait for SITL and FastAPI start
        # max_tries = 10
        # tries = 0
        # while tries < max_tries:
        #     sleep(1)
        #     connection_test = requests.get(f"{api_url}/telemetry/sys_status")
        sleep(10)
        print(f"-----STARTING UAV-{uav_sysid} SETUP-----")

        # Arming uav
        print("Arming...")
        arm_result = requests.get(f"{api_url}/command/arm")
        if arm_result.status_code != 200:
            terminate()
            raise Exception(F"UAV {uav_sysid} not armed")
        print("Armed.")

        # Taking-off uav
        print("Taking off...")
        takeoff_result = requests.get(f"{api_url}/command/takeoff", params={"alt": 15})
        if takeoff_result.status_code != 200:
            terminate()
            raise Exception(f"UAV {uav_sysid} takeoff fail")
        print("Took off.")

        # Going to start position
        print("Going to start position...")
        pos = [int(value) for value in uav_args["pos"][i].strip("[]").split(",")]
        if pos != [0,0,0]:
            pos_data = {"x": pos[0], "y": pos[1], "z": -pos[2]} # in this step we buld the json data and convert z in protocol frame to z in ned frame (downwars)
            go_to_result = requests.post(f"{api_url}/movement/go_to_ned_wait", json=pos_data)
            if go_to_result.status_code != 200:
                terminate()
                msg = f"UAV {uav_sysid} movement to intial position fail"
                raise Exception(msg)
            print("Arrived.")
        print(f"-----UAV-{uav_sysid} SETUP COMPLETED-----")
    print("----------PROTOCOL SETUP COMPLETED----------")
    
    # Stating simulation
    print("----------STARTING PROTOCOL SIMULATION----------")
    for i in range(uav_args["n"]):
        protocols[i].initialize()
    print("----------PROTOCOL SIMULATION STARTED SUCCESSFULLY----------")

if args.protocol:
    timers = [[] for i in range(uav_args["n"])]
    time = 0

    # Simulation loop
    while True:
        for i in range(uav_args["n"]):
            api_port = str(int(uav_args['api_port']) + i)
            api_url = f"http://localhost:{api_port}"
            protocol = protocols[i]

            # Timer handling
            timers[i].extend(protocol.provider.collect_timers())
            new_timer_list = []
            for timer in timers[i]:
                if timer[1] <= time:
                    protocol.handle_timer(timer[0])
                else:
                    new_timer_list.append(timer)
            timers[i] = new_timer_list
            protocol.provider.time = time

            # Telemetry handling
            # uav_pos_result = requests.get(f"{api_url}/telemetry/ned")
            # if uav_pos_result.status_code != 200:
            #     terminate()
            #     raise Exception("Error getting position telemetry")
            # ned_position = uav_pos_result.json()
            # telemetry_msg = Telemetry(current_position=Position(ned_position[0], ned_position[1], -ned_position[2]))
            # protocol.handle_telemetry(telemetry_msg)
        time += 0.01
        sleep(0.01)
else:
    cmd = ""
    while cmd != "stop":
        cmd = input("Digite um comando")
terminate()