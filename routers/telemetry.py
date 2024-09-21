from fastapi import APIRouter, Depends, HTTPException
from copter import Copter
from copter_connection import get_copter_instance
from classes.pos import GPS_pos, Local_pos

telemetry_router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"]
)

@telemetry_router.get("/gps_position", tags=["telemetry"], summary="Returns the copter current GPS position")
def gps_position(uav: Copter = Depends(get_copter_instance)):
    try:
        mav_pos = uav.mav.location()
        print(mav_pos)
        pos = GPS_pos(lat=mav_pos.lat, long=mav_pos.lng, alt=mav_pos.alt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GET_GPS_POSITION FAIL: {e}")
    return {"result": "Success", "lat": pos.lat, "long": pos.long, "alt": pos.alt}

@telemetry_router.get("/local_position", tags=["telemetry"], summary="Returns the copter current NEU position")
def gps_position(uav: Copter = Depends(get_copter_instance)):
    try:
        pos = uav.get_ned_position()
        pos.z = -pos.z # from NED to NEU
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GET_NED_POSITION FAIL: {e}")
    return {"result": "Success", "x": pos.x, "y": pos.y, "z": pos.z}