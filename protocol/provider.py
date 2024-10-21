from protocol.interface import IProvider
from protocol.messages.mobility import MobilityCommand, MobilityCommandType
from protocol.messages.communication import CommunicationCommand, CommunicationCommandType
import requests

class UavControlProvider(IProvider):
    def _provider_report(self, txt):
        print(f"[PROVIDER-{self.id}] {txt}")

    def __init__(self, sysid, api_url, collaborators):
        self.id = sysid
        self.api_url = api_url
        self.timers = []
        self.time = -1
        self.collaborators: dict = collaborators
        self._provider_report(collaborators)

    def send_communication_command(self, command: CommunicationCommand) -> None:
        if command.command_type == CommunicationCommandType.SEND:
            if command.destination not in self.collaborators.keys():
                self._provider_report(f"Destination {command.destination} not found in collaborators's UAV list.\nIgnoring command...")
                return
            message_result = requests.get(f"{self.collaborators[command.destination]}/protocol/message", params={"packet": command.message})
            print(self.collaborators[command.destination])
            if message_result.status_code != 200:
                self._provider_report(f"Unable to send message to UAV api at address: {self.collaborators[command.destination]}")
                return
            self._provider_report(f"Message sent successfully to address: {self.collaborators[command.destination]}")
        elif command.command_type == CommunicationCommandType.BROADCAST:
            for c_sysid, c_api in self.collaborators.items():
                message_result = requests.get(f"{c_api}/protocol/message", params={"packet": command.message})
                if message_result.status_code != 200:
                    self._provider_report(f"Unable to send broadcast message to UAV {c_sysid} api at addres: {c_api}")
                    continue
                self._provider_report(f"Broadcast message sent successfully to: (sysid={c_sysid},api{c_api})")

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