import os
from time import sleep
def start_api(port):
    print(f"Starting API on port {port}...")
    os.system(f"python3 uav_api.py --port {port} --simulated true &")

start_api(8000)
while True:
    print("Protocol running...")
    sleep(2)
