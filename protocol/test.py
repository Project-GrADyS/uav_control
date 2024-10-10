from protocol.messages.mobility import GotoCoordsMobilityCommand
from protocol.interface import IProtocol
from time import sleep

class TestProtocol(IProtocol):

    def initialize(self) -> None:
        self.provider.send_mobility_command(GotoCoordsMobilityCommand(100,100,50))

    def finish(self) -> None:
        pass