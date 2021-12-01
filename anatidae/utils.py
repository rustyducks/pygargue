from dataclasses import dataclass
from enum import Enum

@dataclass
class UDPConnexion:
    name: str
    addr: str
    port: int
    local_addr: str
    local_port: int
    rid: str
    allowed: [str]


