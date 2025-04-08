from contextlib import asynccontextmanager
import os
import uvicorn
from multiprocessing import Process
from fastapi import FastAPI
from routers.protocol import protocol_router
from protocol_connection import set_protocol_queue, get_protocol_queue
from uav_args import parse_args
from protocol_runner import initialize_protocol_runner

# ARGUMENTS
#args = parse_args()

protocol_id = 10
protocol_url = "http://localhost:8000"
protocol_pos = [0, 0, 50]

def start_uav_api(port):
    print(f"Starting UAV API on port {port}...")
    os.system(f"python3 uav_api.py --port {port} --simulated true &")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Starting UAV Control API...
    start_uav_api(8000)

    # Starting Protocol API...
    set_protocol_queue()
    protocol_queue = get_protocol_queue()
    protocol_process = Process(target=initialize_protocol_runner, args=(protocol_queue, protocol_id, protocol_pos, protocol_url, "TelemetryProtocol"))
    protocol_process.start()
    yield
    protocol_queue.put({"type": "finish"})
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
    lifespan=lifespan,
)
app.include_router(protocol_router, prefix="/protocol", tags=["protocol"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")