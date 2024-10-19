from argparse import ArgumentParser
from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry
import requests
from protocol.provider import UavControlProvider
import time
import heapq
import importlib
import os
import heapq

TICK_INTERVAL = 0.05 # Interval between telemetry calls in seconds

def protocol_print(txt):
    global sysid
    print(f"[PROTOCOL-{sysid}] {txt}")

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
        return module.Protocol
    except FileNotFoundError:
        protocol_print("Error: File not found at ~/.config/gradys/protocol.txt")
    except PermissionError:
        protocol_print("Error: Permission denied when trying to access the file")
    except Exception as e:
        protocol_print(f"An error occurred: {e}")

def setup():
    global sysid, api, pos
    protocol_print(f"-----STARTING UAV-{sysid} SETUP-----")
    # Arming uav
    protocol_print("Arming...")
    print("API", api)
    print("SYSID", sysid)
    arm_result = requests.get(f"{api}/command/arm")
    if arm_result.status_code != 200:
        raise Exception(F"UAV {sysid} not armed")
    protocol_print("Armed.")

    # Taking-off uav
    protocol_print("Taking off...")
    takeoff_result = requests.get(f"{api}/command/takeoff", params={"alt": 15})
    if takeoff_result.status_code != 200:
        raise Exception(f"UAV {sysid} takeoff fail")
    protocol_print("Took off.")

    # Going to start position
    protocol_print("Going to start position...")
    pos = [int(value) for value in pos.strip("[]").split(",")]
    if pos != [0,0,0]:
        pos_data = {"x": pos[0], "y": pos[1], "z": -pos[2]} # in this step we buld the json data and convert z in protocol frame to z in ned frame (downwars)
        go_to_result = requests.post(f"{api}/movement/go_to_ned_wait", json=pos_data)
        if go_to_result.status_code != 200:
            msg = f"UAV {sysid} movement to intial position fail"
            raise Exception(msg)
        protocol_print("Arrived.")
    print(f"-----UAV-{sysid} SETUP COMPLETED-----")

def start_execution():
    global started, protocol
    protocol_print("Starting Execution.")
    protocol.initialize()
    started = True

def timer_handler():
    global protocol, protocol_time, timers
    print("timers", timers)
    # Timer Handling
    protocol.provider.time = protocol_time
        
    new_timers = protocol.provider.collect_timers()
    for timer in new_timers:
        heapq.heappush(timers, timer)
    if len(timers) == 0:
        return
    next_timer = timers[0]
    if protocol_time >= next_timer[0]:
        protocol.handle_timer(next_timer[1])
        heapq.heappop(timers)

def telemetry_handler():
    global protocol, api
    # Telemetry Handling
    ned_result = requests.get(f"{api}/telemetry/ned")
    if ned_result.status_code != 200:
        raise Exception("Fail to get NED Telemetry")
    ned_pos = ned_result.json()["info"]["position"]
    telemetry_msg = Telemetry((ned_pos["x"], ned_pos["y"], ned_pos["z"]))
    protocol.handle_telemetry(telemetry_msg)

def queue_handler():
    global protocol, sysid, api, pos, queue
    try:
        command = queue.get(block=False)
    except:
        return
    protocol_print(f"command: {command}")
    if command["type"] == "setup":
        setup()
    elif command["type"] == "start":
        start_execution()
    elif command["type"] == "message":
        protocol.handle_packet(command["packet"])
        
def do_tick():
    timer_handler()
    telemetry_handler()
    queue_handler()

def start_protocol(protocol_name, api_arg, sysid_arg, pos_arg, extern_queue):
    global started, protocol, api, sysid, queue, pos, timers, protocol_time

    protocol_class = get_protocol(protocol_name)
    api = api_arg
    sysid = sysid_arg
    pos = pos_arg
    queue = extern_queue
    timers = []
    provider: IProvider = UavControlProvider(sysid, api)
    protocol = protocol_class.instantiate(provider)
    protocol_time = 0
    
    print(f"Starting Protocol process for UAV {sysid}...")


    # wait for setup and started commands
    started = False
    while not started:
        queue_handler()
        time.sleep(1)
    protocol_print("started")
    last_tick = - TICK_INTERVAL
    while started:
        time_start = time.time()
        if protocol_time >= last_tick + TICK_INTERVAL:  
            print("PROTOCOL-TIME", protocol_time)
            do_tick()
            last_tick = protocol_time
        time_end = time.time()
        protocol_time += time_end - time_start