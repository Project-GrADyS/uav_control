from argparse import ArgumentParser
import os
import requests

parser = ArgumentParser()

parser.add_argument(
    '--n',
    dest='n',
    type=int,
    default=1,
    help="Number of simulated UAVs"
)

parser.add_argument(
    '--protocol',
    dest='protocol_names',
    default=['TimeProtocol'],
    help="Protocol to be used in each UAV. The number of values passed must be equal to 'n'.",
    nargs='*'
)

parser.add_argument(
    '--pos',
    dest='pos_list',
    default=['[0,0,50]'],
    help="Initial position for each UAV. The number of values passed must be equal to 'n'.",
    nargs='*'
)

args = parser.parse_args()

for i in range(args.n):
    connection = f"127.0.0.1:17{171 + i}"
    port = 8000 + i
    sysid = 10 + i
    collaborators = ' '.join([f"[{10+j},http://localhost:{8000+j}]" for j in range(args.n) if j != i])
    uav_command = f"python3 uav_api.py --simulated true --protocol true --sysid {sysid} --pos {args.pos_list[i]} --uav_connection {connection} --port {port} --protocol_name {args.protocol_names[i]} --collaborators {collaborators} &"
    os.system(uav_command)

cmd = ""
while cmd != "stop_protocol":
    cmd = input()
    if cmd == "setup":
        for i in range(args.n):
            result = requests.get(f"http://localhost:{8000+i}/protocol/setup")
    if cmd == "start":
        for i in range(args.n):
            result = requests.get(f"http://localhost:{8000+i}/protocol/start")