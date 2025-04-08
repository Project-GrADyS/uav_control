from contextlib import asynccontextmanager
import os
import uvicorn
from time import sleep
from multiprocessing import Process
import multiprocessing
from fastapi import FastAPI
from routers.protocol import protocol_router
from protocol_connection import set_protocol_queue

# ARGUMENTS
protocol_id = 1
protocol_url = "localhost:8000"


def start_uav_api(port):
    print(f"Starting UAV API on port {port}...")
    os.system(f"python3 uav_api.py --port {port} --simulated true &")

def start_protocol(protocol_queue):
    alive = True
    while alive:
        print("Handling queue.")
        command = {}
        try:
            command = protocol_queue.get_nowait()
        except multiprocessing.queues.Empty:
            sleep(2)
            continue

        print(f"COMMAND RECEIVED: {command}")
        if command["type"] == "setup":
            print("Command is setup.")
            
        elif command["type"] == "start":
            print("Command is start.")
            
        elif command["type"] == "finish":
            print("Command is finish.")
            alive = False
            
        elif command["type"] == "message":
            print("Command is message.")


# Starting UAV API...
start_uav_api(8000)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_uav_api(8000)
    
    protocol_queue = multiprocessing.Queue()
    set_protocol_queue(protocol_queue)

    # Starting Protocol API...
    protocol_process = Process(target=start_protocol, args=(protocol_queue,))
    protocol_process.start()
    yield
    protocol_process.join()

metadata = [{
        "name": "protocol",
        "description": "Provides interface for controlling protocol execution"
    }]

description = f"""
## PROTOCOL INFORMATION
* PROTOCOL_ID = **{protocol_id}**
* UAV_ENDPOINT = **{protocol_url}**
"""
app = FastAPI(
    title="PROTOCOL API",
    description=description,
    version="1.0.0",
    openapi_tags=metadata,
)
app.include_router(protocol_router, prefix="/protocol", tags=["protocol"])

uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")