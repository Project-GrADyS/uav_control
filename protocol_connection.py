from multiprocessing import Queue

p_queue = None

def set_protocol_queue():
    global p_queue
    p_queue = Queue()

def get_protocol_queue():
    global p_queue
    return p_queue