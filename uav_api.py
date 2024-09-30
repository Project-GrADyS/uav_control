import os
from fastapi import FastAPI
from copter_connection import get_copter_instance
from routers.command import command_router
from routers.mission import mission_router
from routers.movement import movement_router
from routers.telemetry import telemetry_router
env = os.environ

copter = get_copter_instance(env["SYSID"], env["UDP_PORT"])

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

app = FastAPI(
    title="UavControl API",
    summary="API designed to simplify Copter control with Ardupilot",
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