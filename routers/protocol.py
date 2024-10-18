from fastapi import APIRouter, Depends
import os
from protocol_queue import get_protocol_queue
import signal

protocol_router = APIRouter(
    prefix="/protocol",
    tags=["protocol"],
)

@protocol_router.get("/setup", tags=["protocol"], summary="Setup UAV for protocol execution, this include going to the start position")
def setup(protocol_queue = Depends(get_protocol_queue)):
    protocol_queue.put({"type": "setup"})

@protocol_router.get("/start", tags=["protocol"], summary="Start UAV protocol execution")
def start(protocol_queue = Depends(get_protocol_queue)):
    protocol_queue.put({"type": "start"})