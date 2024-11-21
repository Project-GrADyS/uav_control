import os
import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager
from uav_args import parse_args
from copter_connection import get_copter_instance
from routers.movement import movement_router
from routers.command import command_router
from routers.telemetry import telemetry_router
from routers.protocol import protocol_router
from protocol_connection import create_protocol
from log import set_log_config

args = parse_args()

if __name__ == '__main__':      
    uvicorn.run("uav_api:app", host="0.0.0.0", port=int(args.port), log_level="info", reload=True)
    exit()

metadata = [
    {
        "name": "movement",
        "description": "Provides GUIDED movement commands for UAV"
    },
    {
        "name": "command",
        "description": "Provides general GUIDED commands for UAV"
    },
    {
        "name": "telemetry",
        "description": "Provides telemetry of the UAV"
    },
    {
        "name": "protocol",
        "description": "Provides interface for controlling protocol execution"
    }
    # {
    #     "name": "mission",
    #     "description": "Provides interface for utilizing ardupilot's built-in navigation with AUTO mode"
    # }
]

description = f"""
## COPTER INFORMATION
* SYSID = **{args.sysid}**
* CONNECTION_STRING = **{args.uav_connection}**
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure loggers
    set_log_config(args)
    # Start SITL
    if args.simulated:
        sitl_command = f"xterm -e {args.ardupilot_path}/Tools/autotest/sim_vehicle.py -v ArduCopter -I {args.sysid} --sysid {args.sysid} -N -L {args.location} --speedup {args.speedup} --out {args.uav_connection} {' '.join([f'--out {address}' for address in args.gs_connection])} &"
        os.system(sitl_command)
    # Initialize protocol thread
    if args.protocol:
        protocol_debug = ("PROTOCOL" in args.debug)
        protocol_console = ("PROTOCOL" in args.log_console)
        protocol_t, protocol_q = create_protocol(args.protocol_name, args.port, args.sysid, args.pos, args.collaborators, args.log_path, protocol_debug, protocol_console, args.communication_range, args.speedup)
    get_copter_instance(args.sysid, f"{args.connection_type}:{args.uav_connection}")
    yield
    # Close protocol thread
    if args.protocol:
        protocol_q.put({"type": "end"})
        protocol_t.join()
    # Close SITL
    if args.simulated:
        os.system("pkill xterm")

app = FastAPI(
    title="UavControl API",
    summary=f"API designed to simplify Copter control with Ardupilot",
    description=description,
    version="0.0.1",
    contact={
        "name": "Francisco Fleury",
        "email": "franmeifleury@gmail.com",
    },
    openapi_tags=metadata,
    lifespan=lifespan
)
app.include_router(movement_router)
app.include_router(command_router)
app.include_router(telemetry_router)
if args.protocol:
    app.include_router(protocol_router)