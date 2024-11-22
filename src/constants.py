from dataclasses import dataclass
from typing import Optional


@dataclass
class SelfbotData:
    token: Optional[str] = None
    # other information here...