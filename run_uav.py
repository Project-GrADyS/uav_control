import os
from argparse import ArgumentParser
from copter_connection import get_copter_instance
from subprocess import Popen
parser = ArgumentParser()

parser.add_argument(
    '--uav_sysid',
    dest='uav_sysid',
    default=-1,
    help="Value for uav SYSID to connect through mavlink",  
)
parser.add_argument(
    '--uav_udp_port',
    dest='uav_udp_port',
    default=-1,
    help="Value for uav UAV on localhost",  
)
# parser.add_argument(
#     '--uav_api_port',
#     dest='uav_api_port',
#     default=-1,
#     help="Value for uav FastAPI port on localhost"
# )

args = parser.parse_args()

if (args.uav_sysid == -1) or (args.uav_udp_port == -1):
    print("Bad parameters. Check uav_sysid and uav_udp_port")
    os.sys.exit(1)

sitl_command = f'xterm -e ~/gradys/ardupilot/Tools/autotest/sim_vehicle.py -v ArduCopter -I {args.uav_sysid} --sysid {args.uav_sysid} -N -L AbraDF --out 127.0.0.1:{args.uav_udp_port} &'
os.system(sitl_command)

api_command = "fastapi dev uav_api.py"
api_command = api_command.split(" ")

env = os.environ.copy()
env["UAV_SYSID"] = args.uav_sysid
env["UAV_UDP_PORT"] = args.uav_udp_port
api_process = Popen(api_command, env=env)

shell_cmd = ""
while shell_cmd != "exit":
    shell_cmd = input()

api_process.terminate()