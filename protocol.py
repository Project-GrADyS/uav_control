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

TICK_INTERVAL = 0.05 # Interval between telemetry calls in seconds

def protocol_print(txt):
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
    protocol_print(f"-----STARTING UAV-{args.sysid} SETUP-----")
    # Arming uav
    protocol_print("Arming...")
    arm_result = requests.get(f"{args.api}/command/arm")
    if arm_result.status_code != 200:
        raise Exception(F"UAV {args.sysid} not armed")
    protocol_print("Armed.")

    # Taking-off uav
    protocol_print("Taking off...")
    takeoff_result = requests.get(f"{args.api}/command/takeoff", params={"alt": 15})
    if takeoff_result.status_code != 200:
        raise Exception(f"UAV {args.sysid} takeoff fail")
    protocol_print("Took off.")

    # Going to start position
    protocol_print("Going to start position...")
    pos = [int(value) for value in args.pos.strip("[]").split(",")]
    if pos != [0,0,0]:
        pos_data = {"x": pos[0], "y": pos[1], "z": -pos[2]} # in this step we buld the json data and convert z in protocol frame to z in ned frame (downwars)
        go_to_result = requests.post(f"{args.api}/movement/go_to_ned_wait", json=pos_data)
        if go_to_result.status_code != 200:
            msg = f"UAV {args.sysid} movement to intial position fail"
            raise Exception(msg)
        protocol_print("Arrived.")
    print(f"-----UAV-{args.sysid} SETUP COMPLETED-----")

def start_execution():
    protocol_print("Starting Execution.")
    protocol.initialize()
    tick_task["timer"] = 1
    tick_task["telemetry"] = 1
    started = True

def timer_handler():
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
    # Telemetry Handling
    ned_result = requests.get(f"{api}/telemetry/ned")
    if ned_result.status_code != 200:
        raise Exception("Fail to get NED Telemetry")
    ned_pos = ned_result.json()["info"]["position"]
    telemetry_msg = Telemetry((ned_pos["x"], ned_pos["y"], ned_pos["z"]))
    protocol.handle_telemetry(telemetry_msg)

def queue_handler():
    command = queue.get()
    if command["type"] == "setup":
        setup()
    elif command["type"] == "start":
        start_execution()
        
def execute_tasks():
    for task, on in tick_task.items():
        if on:
            command_table[task]

def start_protocol(protocol_name, api, sysid, pos, queue):
    print(f"Starting Protocol process for UAV {sysid}...")
    protocol_class = get_protocol(protocol_name)

    provider: IProvider = UavControlProvider(args.sysid, args.api)
    protocol = protocol_class.instantiate(provider)

    command_table = {
        "timer": timer_handler,
        "telemetry": telemetry_handler,
        "consume_queue": queue_handler
    }
    tick_task = {
        "timer": 0,
        "telemetry": 0,
        "consume_queue": 0
    }

    # wait for setup and started commands
    while not started:
        queue_handler()
        sleep(1)
    protocol_time = 0
    last_tick = - TICK_INTERVAL
    while True:
        time_start = time.process_time()
        if protocol_time >= last_tick + TICK_INTERVAL:    
            execute_tasks()
        time_end = time.process_time()
        time += time_end - time_start