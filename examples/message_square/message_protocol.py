from protocol.messages.mobility import GotoCoordsMobilityCommand
from protocol.messages.communication import SendMessageCommand, BroadcastMessageCommand
from protocol.interface import IProtocol
from protocol.messages.telemetry import Telemetry

class Protocol(IProtocol):

    def _protocol_report(self, txt):
        print(f"[MESSAGE PROTOCOL {self.provider.get_id()}] {txt}")

    def initialize(self) -> None:
        # Send message to next uav
        self.provider.send_communication_command(BroadcastMessageCommand(f"Hell friend, Im {self.provider.get_id()}"))
    
    def handle_packet(self, message: str) -> None:
        self._protocol_report("Message received!\n"+message)
    
    def handle_telemetry(self, telemetry: Telemetry) -> None:
        pass

    def handle_timer(self, timer)-> None:
        pass

    def finish(self) -> None:
        pass