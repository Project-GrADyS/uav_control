from multiprocessing import Queue

p_queue = None

def set_protocol_queue(queue: Queue):
    global p_queue
    p_queue = queue

def get_protocol_queue():
    global p_queue
    return p_queue