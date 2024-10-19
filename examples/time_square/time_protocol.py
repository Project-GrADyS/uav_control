from protocol.messages.mobility import GotoCoordsMobilityCommand
from protocol.interface import IProtocol, IProvider
from protocol.messages.telemetry import Telemetry

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
        self.provider.schedule_timer("next_point", self.provider.current_time() + 20)

    def handle_timer(self, timer: str) -> None:
        if timer == "next_point":
            self._go_to_next_point()
            if self.next_point_id != self.id:
                self.provider.schedule_timer("next_point", self.provider.current_time() + 20)
    def handle_telemetry(self, telemetry: Telemetry) -> None:
        pass

    def handle_packet(self, message: str) -> None:
        print("-----MESSAGE RECEIVED-----")
        print(message)

    def finish(self) -> None:
        pass