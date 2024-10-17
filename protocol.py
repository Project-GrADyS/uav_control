from argparse import ArgumentParser
from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry
import requests
from protocol.provider import UavControlProvider
from time import time
import heapq
import importlib
import os
from time import sleep
import signal

TELEMETRY_INTERVAL = 0.1 # Interval between telemetry calls in seconds

def get_protocol(protocol_name: str) -> IProtocol:
    protocol_path = None
    try:
        file_path = os.path.expanduser('~/.config/gradys/protocol.txt')
        with open(file_path, 'r') as file:
            for line in file:
                p_name, p_class = line.strip().split(" ")
                if p_name == protocol_name:
                    protocol_path = p_class
                    break
        if protocol_path == None:
            return None
        module = importlib.import_module(protocol_path)
        print(module)
        return module.Protocol
    except FileNotFoundError:
        print("Error: File not found at ~/.config/gradys/protocol.txt")
    except PermissionError:
        print("Error: Permission denied when trying to access the file")
    except Exception as e:
        print(f"An error occurred: {e}")

parser = ArgumentParser()

parser.add_argument(
    '--sysid',
    dest='sysid',
    type=int,
    required=True,
    help='SYSID of UAV'
)

parser.add_argument(
    '--api',
    dest='api',
    required=True,
    help="Addres of UAV API for movement and telemetry"
)

parser.add_argument(
    '--pos',
    dest='pos',
    required=True,
    help="Initial position of UAV in protocol execution"
)

parser.add_argument(
    '--protocol',
    dest='protocol',
    required=True,
    help="Name of Protocol to run"
)

args = parser.parse_args()


protocol_class = get_protocol(args.protocol)

provider: IProvider = UavControlProvider(args.sysid, args.api)
protocol = protocol_class.instantiate(provider)


def setup():
    print(f"-----STARTING UAV-{args.sysid} SETUP-----")
    # Arming uav
    print("Arming...")
    arm_result = requests.get(f"{args.api}/command/arm")
    if arm_result.status_code != 200:
        raise Exception(F"UAV {args.sysid} not armed")
    print("Armed.")

    # Taking-off uav
    print("Taking off...")
    takeoff_result = requests.get(f"{args.api}/command/takeoff", params={"alt": 15})
    if takeoff_result.status_code != 200:
        raise Exception(f"UAV {args.sysid} takeoff fail")
    print("Took off.")

    # Going to start position
    print("Going to start position...")
    pos = [int(value) for value in args.pos.strip("[]").split(",")]
    if pos != [0,0,0]:
        pos_data = {"x": pos[0], "y": pos[1], "z": -pos[2]} # in this step we buld the json data and convert z in protocol frame to z in ned frame (downwars)
        go_to_result = requests.post(f"{args.api}/movement/go_to_ned_wait", json=pos_data)
        if go_to_result.status_code != 200:
            msg = f"UAV {args.sysid} movement to intial position fail"
            raise Exception(msg)
        print("Arrived.")
    print(f"-----UAV-{args.sysid} SETUP COMPLETED-----")

def start_protocol():
    protocol.initialize()

    timers = []
    protocol_time = 0
    timestamp = time()
    telemetry_timestamp = 0
    while True:
        now = time()
        protocol_time += now - timestamp
        protocol.provider.time = protocol_time
        
        # Timer Handling
        new_timers = protocol.provider.collect_timers()
        for timer in new_timers:
            heapq.heappush(timers, timer)
        if len(timers) != 0:
            next_timer = timers[0]
            if protocol_time >= next_timer[0]:
                print(f"[PROTOCOL PROCCESS] calling handle timer {next_timer[1]}")
                protocol.handle_timer(next_timer[1])
                heapq.heappop(timers)

        # Telemetry Handling
        if protocol_time >= (telemetry_timestamp + TELEMETRY_INTERVAL):
            ned_result = requests.get(f"{args.api}/telemetry/ned")
            if ned_result.status_code != 200:
                raise Exception("Fail to get NED Telemetry")
            ned_pos = ned_result.json()["info"]["position"]
            telemetry_msg = Telemetry((ned_pos["x"], ned_pos["y"], ned_pos["z"]))
            protocol.handle_telemetry(telemetry_msg)
            telemetry_timestamp = protocol_time
        timestamp = now        

print(f"Starting Protocol process for UAV {args.sysid}")

command_table = {
    "setup": setup,
    "start": start_protocol,
}
command_task = {
    "setup": 0,
    "start": 0
}

def handler(signum, frame):
    print('Signal Number: ', signum, " Frame: ", frame)
    if signum == signal.SIGUSR1:
        command_task["setup"] = 1
    elif signum == signal.SIGUSR2:
        command_task["start"] = 1

signal.signal(signal.SIGUSR1, handler)
signal.signal(signal.SIGUSR2, handler)

def execute_tasks():
    for task, on in command_task.items():
        if on:
            command_table[task]()
            command_task[task] = 0

print ("[PROTOCOL] PID =", os.getpid())
while True:
    signal.pause()
    execute_tasks()