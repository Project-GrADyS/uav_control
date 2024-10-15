from protocol.interface import IProvider
from protocol.messages.mobility import MobilityCommand, GotoCoordsMobilityCommand, GotoGeoCoordsMobilityCommand, MobilityCommandType
import requests

class UavControlProvider(IProvider):
    def __init__(self, sysid, api_url):
        self.id = sysid
        self.api_url = api_url
        self.timers = []
        self.time = -1

    # def send_communication_command(self, command: CommunicationCommand) -> None:
    #     """
    #     Sends a communication command to the node's communication module

    #     Args:
    #         command: the communication command to send
    #     """
    #     pass

    def send_mobility_command(self, command: MobilityCommand) -> None:
        if command.command_type == MobilityCommandType.GOTO_COORDS:
            data = {
                "x": command.param_1,
                "y": command.param_2,
                "z": -command.param_3
            }
            requests.post(self.api_url+"/movement/go_to_ned", json=data)
        elif command.command_type == MobilityCommandType.GOTO_GEO_COORDS:
            data = {
                "lat": command.param_1,
                "long": command.param_2,
                "alt": command.param_3
            }
            requests.post(self.api_url+"/movement/go_to_gps", json=data)
    def schedule_timer(self, timer: str, timestamp: float) -> None:
        self.timers.append((timestamp, timer))

    # def cancel_timer(self, timer: str) -> None:
    #     """
    #     Cancels a timer that was previously scheduled. If a timer with the given identifier is not scheduled,
    #     this method does nothing. If multiple timers with the same identifier are scheduled, all of them are canceled.

    #     Args:
    #         timer: identifier of the timer to cancel
    #     """
    #     pass

    def current_time(self) -> float:
        return self.time
    def get_id(self) -> int:
        """
        Returns the node's unique identifier in the simulation

        Returns:
            the node's unique identifier in the simulation
        """
        return self.id

    def collect_timers(self):
        current_timers = self.timers
        self.timers = []
        return current_timers

        # TODO: Document this