from fastapi import APIRouter, Depends, HTTPException
from copter import Copter
from copter_connection import get_copter_instance
from classes.pos import GPS_pos, Local_pos

movement_router = APIRouter(
    prefix = "/movement",
    tags = ["movement"],
)

@movement_router.post("/go_to_gps/", tags=["movement"], summary="Moves the copter to specified GPS position")
def go_to_gps(pos: GPS_pos, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.change_mode("GUIDED")
        uav.go_to_gps(pos.lat, pos.long, pos.alt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GO_TO FAIL: {e}")
    return {"result": f"Going to coord ({pos.lat}, {pos.long}, {pos.alt})"}

@movement_router.post("/go_to_gps_wait", tags=["movement"], summary="Moves and waits for the copter to get to specified GPS position")
def go_to_gps_wait(pos: GPS_pos, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.change_mode("GUIDED")
        uav.go_to_gps(pos.lat, pos.long, pos.alt)
        target_loc = uav.mav_location(pos.lat, pos.long, pos.alt)
        uav.wait_location(target_loc, timeout=60)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GO_TO FAIL: {e}")
    return {"result": f"Arrived at coord ({pos.lat}, {pos.long}, {pos.alt})"}

@movement_router.post("/go_to_local", tags=["movement"], summary="Moves to specified NEU position")
def go_to_local(pos: Local_pos, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.change_mode("GUIDED")
        pos.z = -pos.z # from NEU to NED
        uav.go_to_ned(pos.x, pos.y, -pos.z) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GO_TO FAIL: {e}")
    return {"result": f"Going to local coord ({pos.x}, {pos.y}, {pos.z})"}

@movement_router.post("/go_to_local_wait", tags=["movement"], summary="Moves and waits for the copter to get to specified NEU position")
def go_to_local_wait(pos: Local_pos, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.change_mode("GUIDED")
        pos.z = -pos.z # from NEU to NED
        uav.go_to_ned(pos.x, pos.y, pos.z) 
        uav.wait_ned_position(pos)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GO_TO FAIL: {e}")
    return {"result": f"Arrived at local coord ({pos.x}, {pos.y}, {pos.z})"}

@movement_router.post("/drive", tags=["movement"], summary="Drives copter the specified amount in meters")
def drive(pos: Local_pos, uav: Copter = Depends(get_copter_instance)):
    try:
        uav.change_mode("GUIDED")
        pos.z = -pos.z # from NEU to NED
        uav.drive_ned(pos.x, pos.y, pos.z)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DRIVE FAIL: {e}")
    return {"result": "Copter is driving"}