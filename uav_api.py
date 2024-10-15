from fastapi import FastAPI
from args.uav_args import parse_api
from argparse import ArgumentParser
from copter_connection import get_copter_instance
from routers.movement import movement_router
from routers.command import command_router
from routers.telemetry import telemetry_router
import uvicorn

parser = ArgumentParser()
parse_api(parser)
args = parser.parse_args()

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
        "name": "mission",
        "description": "Provides interface for utilizing ardupilot's built-in navigation with AUTO mode"
    }
]

description = f"""
## COPTER INFORMATION
* SYSID = **{args.sysid}**
* CONNECTION_STRING = **{args.uav_connection}**
"""

copter = get_copter_instance(args.sysid, f"{args.connection_type}:{args.uav_connection}")

app = FastAPI(
    title="UavControl API",
    summary=f"API designed to simplify Copter control with Ardupilot",
    description=description,
    version="0.0.1",
    contact={
        "name": "Francisco Fleury",
        "email": "franmeifleury@gmail.com",
    },
    openapi_tags=metadata
)
app.include_router(movement_router)
app.include_router(command_router)
app.include_router(telemetry_router)