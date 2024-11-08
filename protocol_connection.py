from multiprocessing import Process, Queue
from uav_protocol import start_protocol

p_queue = None

def create_protocol(protocol_name, port, sysid, pos, collaborators, log_file, debug, log_console):
    global p_queue
    p_queue = Queue()
    protocol_process = Process(target=start_protocol, args=(protocol_name, f"http://localhost:{port}", sysid, pos, p_queue, collaborators, log_file, debug, log_console))
    protocol_process.start()
    return (protocol_process, p_queue)

def get_protocol_queue():
    global p_queue
    return p_queue