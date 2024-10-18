from multiprocessing import Process, Queue
from uav_protocol import start_protocol

global uav_args
uav_args = None

def set_protocol_args(protocol_name, port, sysid, pos):
    global uav_args
    uav_args = {
        "protocol_name": protocol_name,
        "port": port,
        "sysid": sysid,
        "pos": pos
    }

global p_queue
p_queue = None

def get_protocol_queue():
    global p_queue
    global uav_args
    if uav_args != None:
        p_queue = Queue()
        protocol_process = Process(target=start_protocol, args=(uav_args["protocol_name"], f"http://localhost:{uav_args['port']}", uav_args["sysid"], uav_args["pos"], p_queue))
        protocol_process.start()
        return p_queue
    return None