from argparse import ArgumentParser
from protocol.test import TestProtocol
import requests
from protocol.provider import UavControlProvider
from time import time
import heapq

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

args = parser.parse_args()

provider = UavControlProvider(args.sysid, args.api)
protocol = TestProtocol.instantiate(provider)

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
    while True:
        now = time()
        protocol_time += now - timestamp
        print(protocol_time)
        protocol.provider.time = protocol_time
        new_timers = protocol.provider.collect_timers()
        for timer in new_timers:
            heapq.heappush(timers, timer)
        if len(timers) == 0:
            continue
        next_timer = timers[0]
        if protocol_time >= next_timer[0]:
            print(f"[PROTOCOL PROCCESS] calling handle timer {next_timer[1]}")
            protocol.handle_timer(next_timer[1])
            heapq.heappop(timers)
        timestamp = now
        

print(f"Starting Protocol process for UAV {args.sysid}")

cmd = ""
cmd_list = {
    "setup": setup,
    "start": start_protocol
}
while cmd !="stop":
    cmd = input()
    cmd_list[cmd]()
    
