from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry
from protocol.messages.communication import CommunicationCommandType
from protocol.messages.mobility import MobilityCommandType
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
import asyncio

TIMER_INTERVAL = 0.1   
TELEMETRY_INTERVAL = 0.1
QUEUE_INTERVAL = 0.4
COMMUNICATION_INTERVAL = 0.4
MOBILITY_INTERVAL = 0.2

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

async def timer_handler():
    global protocol, timers, running, speedup
    
    protocol.provider.time = 0
    while running:
        time_start = time.time()
        # Timer Handling
        protocol_print("Handling Timer.")
        new_timers = protocol.provider.collect_timers()
        for timer in new_timers:
            heapq.heappush(timers, timer)
        if len(timers) == 0:
            return
        next_timer = timers[0]
        if protocol.provider.time >= next_timer[0]:
            protocol.handle_timer(next_timer[1])
            heapq.heappop(timers)

        await asyncio.sleep(TIMER_INTERVAL/speedup)
        time_end = time.time()
        protocol.provider.time += (time_end - time_start) * speedup
async def telemetry_handler():
    global protocol, api, running

    while running:
    # Telemetry Handling
        protocol_print(f"Handling telemetry.")
        ned_result = requests.get(f"{api}/telemetry/ned")
        if ned_result.status_code != 200:
            raise Exception("Fail to get NED Telemetry")
        ned_pos = ned_result.json()["info"]["position"]
        coords = [ned_pos["x"], ned_pos["y"], -ned_pos["z"]]
        protocol.provider.current_pos = coords
        telemetry_msg = Telemetry(coords)
        protocol.handle_telemetry(telemetry_msg)

        await asyncio.sleep(TELEMETRY_INTERVAL)

def handle_message(command):
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

def clear_queue(q, max_elements):
    elements = []
    try:
        while len(elements) < max_elements:
            elements.append(q.get_nowait())
    except multiprocessing.queues.Empty:
        print("QUEUE IS EMPTY")
    return elements


async def queue_handler():
    global protocol, queue, running, alive
    
    while alive: 
        protocol_print("Handling queue.")
        command = {}
        try:
            command = queue.get_nowait()
        except multiprocessing.queues.Empty:
            await asyncio.sleep(QUEUE_INTERVAL)
            continue

        protocol_print(f"COMMAND RECEIVED: {command}")
        if command["type"] == "setup":
            setup()
        elif command["type"] == "start":
            running = True
            start_execution()
            return
        elif command["type"] == "finish":
            protocol.finish()
            running = False
        elif command["type"] == "message" and running:
            print("Command is message.")
            handle_message(command)
        elif command["type"] == "end":
            alive = False
            return

# async def send_message(message, pos, api):
#     movement_result = requests.post(f"{api}/protocol/message", params={"packet": message}, json=pos)
#     if movement_result.status_code != 200:
#         protocol_critical(f"Error sending message to {api}")

# async def communication_handler():
#     global protocol, running, colab_table

#     while running:
#         commands = protocol.provider.collect_communication_commands()

#         for command_obj in commands:
#             command = command_obj["command"]
#             if command.command_type == CommunicationCommandType.SEND:
#                 await send_message(command.message, command_obj["uav_pos"], colab_table[command.destination])
#             elif command.command_type == CommunicationCommandType.BROADCAST:
#                 for c_id, c_api in colab_table.items():
#                     await send_message(command.message, command_obj["uav_pos"], c_api)

#         await asyncio.sleep(COMMUNICATION_INTERVAL)

# async def move(api, frame, payload):
#     movement_result = requests.post(f"{api}/movement/go_to_{frame}", json=payload)
#     if movement_result.status_code != 200:
#         protocol_critical("Movement Error.")

# async def mobility_handler():
#     global protocol, running, api

#     while running:
#         commands = protocol.provider.collect_mobility_commands()

#         for command_obj in commands:
#             if command_obj["command"].command_type == MobilityCommandType.GOTO_COORDS:
#                 await move(api, "ned", command_obj["data"])
#             elif command_obj["command"].command_type == MobilityCommandType.GOTO_GEO_COORDS:
#                 await move(api, "gps", command_obj["data"])

#         await asyncio.sleep(MOBILITY_INTERVAL)

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
    global alive, queue, running, protocol
    print("Calling end handler...")
    alive = False
    running = False
    protocol.finish()

def start_protocol(protocol_name, api_arg, sysid_arg, pos_arg, extern_queue, collaborators, log_file, debug, log_console, cr, speed):
    global running, protocol, api, sysid, queue, pos, timers, communication_range, alive, colab_table, speedup

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
    speedup = speed

    signal.signal(signal.SIGINT, end)

    protocol_print(f"Starting Protocol process for UAV {sysid}...")

    alive = True
    running = False

    async def main_loop():
        setup_queue_task = asyncio.create_task(queue_handler())
        
        await setup_queue_task
        
        timer_task = asyncio.create_task(timer_handler())
        telemetry_task = asyncio.create_task(telemetry_handler())
        queue_task = asyncio.create_task(queue_handler())

        await timer_task
        await telemetry_task
        await queue_task
        protocol_print("----- END -----")

    asyncio.run(main_loop())