from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from copter import Copter
from copter_connection import get_copter_instance

command_router = APIRouter(
    prefix = "/command",
    tags = ["command"],
)

class Movement(BaseModel):
    lat: float
    long: float
    alt: int

@command_router.get("/arm", tags=["command"])
def arm(uav: Copter = Depends(get_copter_instance)):
    try:
        uav.change_mode("GUIDED")
        uav.wait_ready_to_arm()
        uav.arm_vehicle()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ARM_COMMAND FAIL: {e}")
    result = "Armed vehicle" if uav.armed() else "Disarmed vehicle"
    return {"result": result}

@command_router.get("/takeoff", tags=["command"])
def takeoff(alt: int = 15, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.user_takeoff(alt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TAKEOFFF_COMMAND FAIL: {e}")
    return {"result": f"Takeoff successful! Vehicle at {alt} meters"}

@command_router.get("/land", tags=["command"])
def land(timeout=60, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.land_and_disarm()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LAND_COMMAND FAIL: {e}")
    return {"result": "Landed at home successfully"}

@command_router.get("/rtl", tags=["command"])
def rlt(uav: Copter = Depends(get_copter_instance)):
    try:
        uav.do_RTL()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RTL_COMMAND FAIL: {e}")
    return {"result": "Landed at home successfully"}