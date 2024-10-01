import os
from argparse import ArgumentParser
from runner import Runner, CopterMode
parser = ArgumentParser()

parser.add_argument(
    '--sysid',
    dest='sysid',
    default=None,
    help="Value for uav SYSID to connect through mavlink",  
)
parser.add_argument(
    '--udp_port',
    dest='udp_port',
    default=None,
    help="Value for uav UDP connection on localhost",  
)

parser.add_argument(
    '--location',
    dest='location',
    default=None,
    help="Value for uav HOME LOCATION"
)

parser.add_argument(
    '--config',
    dest='config',
    default=None,
    help="Config file to extract configurations from"
)
# parser.add_argument(
#     '--uav_api_port',
#     dest='uav_api_port',
#     default=-1,
#     help="Value for uav FastAPI port on localhost"
# )

args = parser.parse_args()

copter_runner = Runner(CopterMode.SIMULATED)
if args.config != None:
    copter_runner.setParamsFromConfig(args.config)
copter_runner.setParams(sysid=args.sysid, udp_port=args.udp_port, location=args.location)
copter_runner.run()