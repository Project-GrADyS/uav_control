import logging
import random

from protocol.plugin.follow_mobility import MobilityFollowerPlugin
from protocol.interface import IProtocol
from protocol.messages.telemetry import Telemetry


class Protocol(IProtocol):
    follower: MobilityFollowerPlugin

    def __init__(self):
        self._logger = logging.getLogger()

    def initialize(self) -> None:
        self.follower = MobilityFollowerPlugin(self)

        self.follower.set_relative_position((
            random.uniform(-5, 5),
            random.uniform(-5, 5),
            random.uniform(0, 5)
        ))

        self.provider.schedule_timer("", 0.1)

    def handle_timer(self, timer: str) -> None:
        if self.follower.current_leader is None and len(self.follower.available_leaders) > 0:
            self.follower.follow_leader(list(self.follower.available_leaders)[0])

        self._logger.info(f"Following leader: {self.follower.current_leader}")

        self.provider.schedule_timer("", self.provider.current_time() + 1)

    def handle_packet(self, message: str) -> None:
        pass

    def handle_telemetry(self, telemetry: Telemetry) -> None:
        pass

    def finish(self) -> None:
        pass