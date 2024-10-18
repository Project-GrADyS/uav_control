from argparse import ArgumentParser
from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry
import requests
from protocol.provider import UavControlProvider
from time import time
import heapq
import importlib
import os
import time
import signal
import heapq

TICK_INTERVAL = 0.05 # Interval between telemetry calls in seconds

def protocol_print(txt):
    print(f"[PROTOCOL] {txt}")

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

def setup(sysid, api, pos):
    protocol_print(f"-----STARTING UAV-{sysid} SETUP-----")
    # Arming uav
    protocol_print("Arming...")
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

def start_execution(protocol):
    protocol_print("Starting Execution.")
    protocol.initialize()
    tick_task["timer"] = 1
    tick_task["telemetry"] = 1
    started = True

def timer_handler(protocol, heapq):
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

def telemetry_handler(protocol, api):
    # Telemetry Handling
    ned_result = requests.get(f"{api}/telemetry/ned")
    if ned_result.status_code != 200:
        raise Exception("Fail to get NED Telemetry")
    ned_pos = ned_result.json()["info"]["position"]
    telemetry_msg = Telemetry((ned_pos["x"], ned_pos["y"], ned_pos["z"]))
    protocol.handle_telemetry(telemetry_msg)

def queue_handler(protocol, sysid, api, pos, queue):
    protocol_print(f"Queue: {queue}")
    command = queue.get()
    protocol_print(f"command: {command}")
    if command["type"] == "setup":
        setup(sysid, api, pos)
    elif command["type"] == "start":
        start_execution(protocol)
        
def do_tick(protocol, api, sysid, timer_heap, extern_queue):
    timer_handler(protocol, timer_heap)
    telemetry_handler(protocol, api)
    queue_handler(protocol, sysid, api, pos, extern_queue)

def start_protocol(protocol_name, api, sysid, pos, extern_queue):
    print(f"Starting Protocol process for UAV {sysid}...")
    protocol_class = get_protocol(protocol_name)

    provider: IProvider = UavControlProvider(sysid, api)
    protocol = protocol_class.instantiate(provider)

    # wait for setup and started commands
    started = False
    while not started:
        queue_handler(protocol, sysid, api, pos, extern_queue)
        sleep(1)

    timer_heap = []
    protocol_time = 0
    last_tick = - TICK_INTERVAL
    while True:
        time_start = time.process_time()
        if protocol_time >= last_tick + TICK_INTERVAL:    
            do_tick(protocol, api, sysid, timer_heap, extern_queue)
        time_end = time.process_time()
        time += time_end - time_start