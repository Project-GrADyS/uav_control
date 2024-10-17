from protocol.messages.mobility import GotoCoordsMobilityCommand
from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry

ACCURACY = 3

class Protocol(IProtocol):
    
    def _go_to_next_point(self):
        self.next_point_id = (self.next_point_id + 1) % 4
        self.next_point = self.points[self.next_point_id]
        self.provider.send_mobility_command(GotoCoordsMobilityCommand(self.next_point[0], self.next_point[1], self.next_point[2]))

    def initialize(self) -> None:
        self.points = [[100,100,50], [100,-100,50], [-100,-100,50], [-100,100,50]]
        self.id = self.provider.get_id() - 10
        self.initial_pos = self.points[self.id]
        self.next_point_id = self.id
        self._go_to_next_point()
    
    def handle_timer(self, timer: str) -> None:
        pass

    def handle_telemetry(self, telemetry: Telemetry) -> None:
        diff = abs(telemetry.current_position[0] - self.next_point[0]) + abs(telemetry.current_position[1] - self.next_point[1]) + abs(telemetry.current_position[2] + self.next_point[2])
        if diff < ACCURACY:
            self._go_to_next_point()
    def finish(self) -> None:
        pass