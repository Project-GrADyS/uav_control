from fastapi import APIRouter, Depends
import os
from protocol_pid import get_protocol_pid
import signal

protocol_router = APIRouter(
    prefix="/protocol",
    tags=["protocol"],
)

@protocol_router.get("/setup", tags=["protocol"], summary="Setup UAV for protocol execution, this include going to the start position")
def setup(p_pid = Depends(get_protocol_pid)):
    print(f"Sending signal USR1 to {p_pid}")
    os.kill(int(p_pid), signal.SIGUSR1)

@protocol_router.get("/start", tags=["protocol"], summary="Start UAV protocol execution")
def start(p_pid = Depends(get_protocol_pid)):
    print(f"Sending signal USR2 to {p_pid}")
    os.kill(int(p_pid), signal.SIGUSR2)