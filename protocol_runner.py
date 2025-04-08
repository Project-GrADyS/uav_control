import multiprocessing
import asyncio
import requests
import logging
import importlib
import os
import time
import heapq
from protocol.interface import IProtocol
from protocol.messages.telemetry import Telemetry
from protocol.provider import UavControlProvider

class ProtocolRunner:

    TIMER_INTERVAL = 0.2
    TELEMETRY_INTERVAL = 0.5
    QUEUE_INTERVAL = 0.5
    #COMMUNICATION_INTERVAL = 0.4
    #MOBILITY_INTERVAL = 0.2

    def __init__(self, protocol_queue, sysid, pos, api, protocol_instance, speedup=1):
        self.running = False
        self.alive = True
        self.queue = protocol_queue
        self.sysid = sysid
        self.pos = pos
        self.api = api
        self.protocol = protocol_instance
        self.scheduled_tasks = []
        self.timers = []
        self.speedup = speedup

    def setup_logger(self, log_file, debug, log_console):        
        self.logger = logging.getLogger("PROTOCOL")
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)

        if log_console:
            console_formatter = logging.Formatter(f"[%(name)s-{self.sysid}] %(levelname)s - %(message)s")
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        if debug:
            self.logger.setLevel("DEBUG")
        else:
            self.logger.setLevel("INFO")

        self.logger.addHandler(file_handler)

    def _protocol_debug(self, txt):
        self.logger.debug(txt)

    def _protocol_print(self, txt):
        self.logger.info(txt)

    def _protocol_critical(self, txt):
        self.logger.critical(txt)

    def setup(self):
        self._protocol_print(f"-----STARTING UAV-{self.sysid} SETUP-----")
        self._protocol_debug(f"API {self.api}")
        self._protocol_debug(f"SYSID {self.sysid}")
        # Arming uav
        self._protocol_print("Arming...")
        arm_result = requests.get(f"{self.api}/command/arm")
        if arm_result.status_code != 200:
            raise Exception(F"UAV {self.sysid} not armed")
        self._protocol_print("Armed.")

        # Taking-off uav
        self._protocol_print("Taking off...")
        takeoff_result = requests.get(f"{self.api}/command/takeoff", params={"alt": 15})
        if takeoff_result.status_code != 200:
            raise Exception(f"UAV {self.sysid} takeoff fail")
        self._protocol_print("Took off.")

        # Going to start position
        self._protocol_print("Going to start position...")
        if self.pos != [0,0,0]:
            pos_data = {"x": self.pos[0], "y": self.pos[1], "z": -self.pos[2]} # in this step we buld the json data and convert z in protocol frame to z in ned frame (downwars)
            go_to_result = requests.post(f"{self.api}/movement/go_to_ned_wait", json=pos_data)
            if go_to_result.status_code != 200:
                msg = f"UAV {self.sysid} movement to intial position fail"
                raise Exception(msg)
            self._protocol_print("Arrived.")
        self._protocol_print(f"-----UAV-{self.sysid} SETUP COMPLETED-----")

    async def telemetry_handling(self):
        while self.running:
            self._protocol_print("Handling telemetry.")
            ned_result = requests.get(f"{self.api}/telemetry/ned")
            if ned_result.status_code != 200:
                raise Exception("Fail to get NED Telemetry")
            ned_pos = ned_result.json()["info"]["position"]
            coords = [ned_pos["x"], ned_pos["y"], -ned_pos["z"]]
            self.protocol.provider.current_pos = coords
            telemetry_msg = Telemetry(coords)
            self.protocol.handle_telemetry(telemetry_msg)
            await asyncio.sleep(self.TELEMETRY_INTERVAL)

    async def timer_handling(self):
        while self.running:
            time_start = time.time()
            # Timer Handling
            self._protocol_print("Handling Timer.")
            new_timers = self.protocol.provider.collect_timers()
            for timer in new_timers:
                heapq.heappush(self.timers, timer)
            if len(self.timers) == 0:
                return
            next_timer = self.timers[0]
            if self.protocol.provider.time >= next_timer[0]:
                self.protocol.handle_timer(next_timer[1])
                heapq.heappop(self.timers)

            await asyncio.sleep(self.TIMER_INTERVAL/self.speedup)
            time_end = time.time()
            self.protocol.provider.time += (time_end - time_start) * self.speedup

    def start_execution(self):
        self._protocol_print(f"-----STARTING UAV-{self.sysid} EXECUTION-----")
        self.running = True

        self.protocol.initialize()

        # Telemetry handler
        self.scheduled_tasks.append(asyncio.create_task(self.telemetry_handling()))
        # Timer handler
        self.scheduled_tasks.append(asyncio.create_task(self.timer_handling()))

    async def finish_execution(self):
        self.running = False
        for task in self.scheduled_tasks:
            await task
        self.scheduled_tasks = []
        # call protocol finish method
        self.alive = False

    def handle_message(self, command):
        pass

    async def start_runner(self):
        while self.alive: 
            self._protocol_print("Handling queue.")
            command = {}
            try:
                command = self.queue.get_nowait()
            except multiprocessing.queues.Empty:
                await asyncio.sleep(self.QUEUE_INTERVAL)
                continue

            self._protocol_print(f"COMMAND RECEIVED: {command}")
            if command["type"] == "setup":
                self.setup()
            elif command["type"] == "start":
                self.start_execution()
            elif command["type"] == "finish":
                await self.finish_execution()
            elif command["type"] == "message" and self.running:
                print("Command is message.")
                self.handle_message(command)

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
        print("Error: File not found at ~/.config/gradys/protocol.txt")
        return None
    except PermissionError:
        print("Error: Permission denied when trying to access the file")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    module = importlib.import_module(protocol_path)
    print(f"MODULE: {module}")
    return module.Protocol

def initialize_protocol_runner(protocol_queue, sysid, pos, api, protocol_name):
    protocol_module = get_protocol(protocol_name)
    if protocol_module is None:
        raise Exception(f"Protocol {protocol_name} not found")
    
    provider = UavControlProvider(sysid, api, {})
    protocol_instance = protocol_module.instantiate(provider)

    runner = ProtocolRunner(protocol_queue, sysid, pos, api, protocol_instance)
    runner.setup_logger("protocol.log", debug=True, log_console=True)
    
    asyncio.run(runner.start_runner())