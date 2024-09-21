import os
from fastapi import FastAPI
from copter_connection import get_copter_instance
from routers.command import command_router
from routers.mission import mission_router
from routers.movement import movement_router
from routers.telemetry import telemetry_router
env = os.environ

copter = get_copter_instance({"uav_sysid": env["UAV_SYSID"], "uav_udp_port": env["UAV_UDP_PORT"]})

app = FastAPI()
app.include_router(movement_router)
app.include_router(command_router)
app.include_router(telemetry_router)
app.include_router(mission_router)