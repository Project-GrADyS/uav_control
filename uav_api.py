import os
from fastapi import FastAPI
from copter_connection import get_copter_instance
from routers.command import command_router
from routers.mission import mission_router
from routers.movement import movement_router
from routers.telemetry import telemetry_router
from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument(
    '--port',
    dest='port',
    default=8000,
    help='Port for api to run on'
)

parser.add_argument(
    '--uav_connection',
    dest='uav_connection',
    default=None,
    help='Address used for copter connection'
)

parser.add_argument(
    '--sysid',
    dest='sysid',
    default=None,
    help='Sysid for Copter'
)

args = parser.parse_args()

if args.uav_connection == None:
    raise Exception("No uav_connection received")

copter = get_copter_instance(args.sysid, args.uav_connection)

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
app.include_router(mission_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("uav_api:app", host="0.0.0.0", port=int(args.port), log_level="info", reload=True)