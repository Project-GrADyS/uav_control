from multiprocessing import Queue

global p_queue
p_queue = None
def get_protocol_queue():
    global p_queue
    if p_queue == None:
        p_queue = Queue()
    return p_queue