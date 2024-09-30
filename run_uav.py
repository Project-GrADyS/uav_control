import os
from argparse import ArgumentParser
from runner import Runner, CopterMode
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

copter_runner = Runner(CopterMode.SIMULATED)
copter_runner.setParams(sysid=args.uav_sysid, udp_port=args.uav_udp_port, location= "AbraDF")
copter_runner.run()