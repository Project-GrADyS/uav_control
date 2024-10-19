from fastapi import APIRouter, Depends
from protocol_connection import get_protocol_queue

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

@protocol_router.get("/message", tags=["protocol"], summary="Send message to UAV protocol")
def send_message(packet: str, protocol_queue = Depends(get_protocol_queue)):
    protocol_queue.put({"type": "message", "packet": packet})