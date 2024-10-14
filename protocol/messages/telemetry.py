from dataclasses import dataclass
from typing import Tuple

Position = Tuple[float, float, float]

@dataclass
class Telemetry:
    current_position: Position