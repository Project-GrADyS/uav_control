global protocol_pid
protocol_pid = -1
def get_protocol_pid(pid = None):
    global protocol_pid
    if pid != None:
        protocol_pid = pid
    return protocol_pid