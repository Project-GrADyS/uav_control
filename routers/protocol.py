from typing import List
from fastapi import APIRouter, Depends
from protocol_connection import get_protocol_queue
from classes.pos import Local_pos

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

@protocol_router.get("/finish", tags=["protocol"], summary="Finish UAV protocol execution")
def finish(protocol_queue = Depends(get_protocol_queue)):
    protocol_queue.put({"type": "finish"})

@protocol_router.post("/message", tags=["protocol"], summary="Send message to UAV protocol")
def send_message(packet: str, pos: Local_pos, protocol_queue = Depends(get_protocol_queue)):
    formatted_pos = (pos.x, pos.y, pos.z)
    print(formatted_pos)
    protocol_queue.put({"type": "message", "packet": packet, "pos": formatted_pos})