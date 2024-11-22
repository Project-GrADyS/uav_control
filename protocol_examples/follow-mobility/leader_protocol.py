import logging

from protocol.plugin.follow_mobility import MobilityFollowerPlugin, MobilityLeaderPlugin
from protocol.plugin.mission_mobility import MissionMobilityPlugin, MissionMobilityConfiguration, LoopMission
from protocol.interface import IProtocol
from protocol.messages.mobility import SetSpeedMobilityCommand
from protocol.messages.telemetry import Telemetry

class Protocol(IProtocol):
    leader: MobilityLeaderPlugin

    def __init__(self):
        self._logger = logging.getLogger()

    def initialize(self) -> None:
        self.leader = MobilityLeaderPlugin(self)

        mission = MissionMobilityPlugin(self, MissionMobilityConfiguration(loop_mission=LoopMission.RESTART))
        mission.start_mission([
            (20, 20, 5),
            (20, -20, 5),
            (-20, -20, 5),
            (-20, 20, 5)
        ])

        #command = SetSpeedMobilityCommand(5)
        #self.provider.send_mobility_command(command)
        self.provider.schedule_timer("", self.provider.current_time() + 1)

    def handle_timer(self, timer: str) -> None:
        self._logger.info(f"Being followed by: {self.leader.followers}")

        self.provider.schedule_timer("", self.provider.current_time() + 1)

    def handle_packet(self, message: str) -> None:
        pass

    def handle_telemetry(self, telemetry: Telemetry) -> None:
        pass

    def finish(self) -> None:
        pass