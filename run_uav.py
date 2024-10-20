import os
from args.uav_args import parse_args
from subprocess import Popen

# Seting up arguments...
args = parse_args()

if args.config != None:
    pass    

if args.simulated:
    # Starting simulation 
    print("simulating...")
    sitl_command = f"xterm -e {args.ardupilot_path}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {args.sysid} --sysid {args.sysid} -N -L {args.location} --speedup {args.speedup} --out {args.uav_connection} {' '.join([f'--out {address}' for address in args.gs_connection])} &"
    os.system(sitl_command)
print(args.collaborators)
api_command = f"python3 uav_api.py --uav_connection {args.uav_connection} --port {args.port} --sysid {args.sysid} --connection_type {args.connection_type} --protocol_name {args.protocol_name} --pos {args.pos} --collaborators {' '.join(args.collaborators)}"
os.system(api_command)