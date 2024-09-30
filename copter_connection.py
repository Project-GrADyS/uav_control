from copter import Copter

copter = None

# in the future this function should use different prefix for connection_string based on CopterMode
def get_copter_instance(sysid=None, udp_port=None):
    global copter
    if copter is None:
        copter = Copter(sysid=int(sysid))
        copter.connect(connection_string=f"udpin:127.0.0.1:{udp_port}")
    return copter