import os
from fastapi import FastAPI
from copter_connection import get_copter_instance
from routers.command import command_router
from routers.mission import mission_router
from routers.movement import movement_router
from routers.telemetry import telemetry_router
from args.uav_args import parse_args
from subprocess import Popen
import uvicorn

# Seting up arguments...
args = parse_args()

if args.config != None:
    pass    

if args.simulated:
    # Starting simulation 
    print("simulating...")
    sitl_command = f"xterm -e {args.ardupilot_path}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {args.sysid} --sysid {args.sysid} -N -L {args.location} --speedup {args.speedup} --out {args.uav_connection} {' '.join([f'--out {address}' for address in args.gs_connection])} &"
    os.system(sitl_command)

if args.protocol:
    protocol_command = f"python3 protocol.py --sysid {args.sysid} --api http://localhost:{args.port} --pos {args.pos}".split(" ")
    protocol_proccess = Popen(protocol_command)


api_command = f"python3 uav_api.py --uav_connection {args.uav_connection} --port {args.port} --sysid {args.sysid} --connection_type {args.connection_type}"
os.system(api_command)