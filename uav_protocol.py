from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry
import requests
from protocol.provider import UavControlProvider
import time
import heapq
import importlib
import os
import heapq
import logging
import math
import multiprocessing
import signal

TICK_INTERVAL = 0.1 # Interval between telemetry calls in seconds

def protocol_debug(txt):
    global logger
    logger.debug(txt)

def protocol_print(txt):
    global logger
    logger.info(txt)

def protocol_critical(txt):
    global logger
    logger.critical(txt)

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

def get_protocol(protocol_name: str) -> IProtocol:
    protocol_path = None
    try:
        file_path = os.path.expanduser('~/.config/gradys/protocol.txt')
        with open(file_path, 'r') as file:
            for line in file:
                p_name, p_class = line.strip().split(" ")
                if p_name == protocol_name:
                    print(p_name, p_class)
                    protocol_path = p_class
                    break
        if protocol_path == None:
            print(f"NO PATH: {protocol_name}")
            return None
    except FileNotFoundError:
        protocol_critical("Error: File not found at ~/.config/gradys/protocol.txt")
        return None
    except PermissionError:
        protocol_critical("Error: Permission denied when trying to access the file")
        return None
    except Exception as e:
        protocol_critical(f"An error occurred: {e}")
        return None
    module = importlib.import_module(protocol_path)
    print(f"MODULE: {module}")
    return module.Protocol

def setup():
    global sysid, api, pos
    protocol_print(f"-----STARTING UAV-{sysid} SETUP-----")
    protocol_debug(f"API {api}")
    protocol_debug(f"SYSID {sysid}")
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
    if pos != [0,0,0]:
        pos_data = {"x": pos[0], "y": pos[1], "z": -pos[2]} # in this step we buld the json data and convert z in protocol frame to z in ned frame (downwars)
        go_to_result = requests.post(f"{api}/movement/go_to_ned_wait", json=pos_data)
        if go_to_result.status_code != 200:
            msg = f"UAV {sysid} movement to intial position fail"
            raise Exception(msg)
        protocol_print("Arrived.")
    protocol_print(f"-----UAV-{sysid} SETUP COMPLETED-----")

def start_execution():
    global running, protocol
    protocol_print("Starting Execution.")
    protocol.initialize()
    running = True

def timer_handler():
    global protocol, protocol_time, timers

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
    coords = [ned_pos["x"], ned_pos["y"], -ned_pos["z"]]
    protocol_print(f"Handling telemetry. (coords={coords})")
    protocol.provider.current_pos = coords
    telemetry_msg = Telemetry(coords)
    protocol.handle_telemetry(telemetry_msg)

def communication_handler(command):
    global protocol, communication_range

    if communication_range == -1:
        protocol.handle_packet(command["packet"])
        return
    protocol_debug(f"message_pos: {command['pos']}")

    uavs_distance = euclidean_distance(command['pos'], protocol.provider.current_pos)
    protocol_debug(f"message_distance: {uavs_distance}")
    if uavs_distance <= communication_range:
        protocol.handle_packet(command["packet"])
        protocol_print(f"Message received!\n{command['packet']}")
    else:
        protocol_print("Message rejected.")

def queue_handler():
    global protocol, sysid, api, pos, queue, running, alive
    items = []
    try:
        while len(items) < 5 and not queue.empty():
            items.append(queue.get_nowait())  # Retrieve item without blocking
    except multiprocessing.queues.Empty:
        pass  # Queue is empty, return what we have

    for command in items:        
        protocol_print(f"ITEMS: {len(items)}; command: {command}")
        if command["type"] == "setup":
            setup()
        elif command["type"] == "start":
            running = True
            start_execution()
        elif command["type"] == "message" and running:
            communication_handler(command)
        elif command["type"] == "finish":
            protocol.finish()
            running = False
        
def do_tick():
    timer_handler()
    telemetry_handler()

def build_collaborator_table(collab_list):
    colab_table = {}
    protocol_debug(f"collab_list {collab_list}")
    for collab in collab_list:
        c_id, c_api = collab.strip("[]").split(",")
        protocol_debug(f"c_id {c_id}")
        protocol_debug(f"c_api {c_api}")
        colab_table[int(c_id)] = c_api
    return colab_table

def setup_logger(log_file, debug, log_console):
    global logger, sysid
    
    logger = logging.getLogger("PROTOCOL")
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)

    if log_console:
        console_formatter = logging.Formatter(f"[%(name)s-{sysid}] %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    if debug:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")

    logger.addHandler(file_handler)

def end(signum, frame):
    global alive, queue
    print("Calling end handler...")
    alive = False
    protocol.finish()

def start_protocol(protocol_name, api_arg, sysid_arg, pos_arg, extern_queue, collaborators, log_file, debug, log_console, cr, speedup):
    global running, protocol, api, sysid, queue, pos, timers, protocol_time, communication_range, alive

    communication_range = float(cr)
    sysid = sysid_arg
    setup_logger(log_file, debug, log_console)
    protocol_class = get_protocol(protocol_name)
    api = api_arg
    pos = pos = [int(value) for value in pos_arg.strip("[]").split(",")]
    queue = extern_queue
    timers = []
    colab_table = build_collaborator_table(collaborators)
    provider: IProvider = UavControlProvider(sysid, api, colab_table)
    provider.current_pos = pos
    protocol = protocol_class.instantiate(provider)
    protocol_time = 0
    
    signal.signal(signal.SIGINT, end)

    protocol_print(f"Starting Protocol process for UAV {sysid}...")

    alive = True
    running = False
    started = False
    last_tick = -TICK_INTERVAL
    while alive:
        time_start = time.time()

        if running:
            if protocol_time >= last_tick + TICK_INTERVAL:  
                do_tick()
                last_tick = protocol_time

        queue_handler()

        time_end = time.time()
        protocol_time += (time_end - time_start) * speedup
    protocol_print("END")