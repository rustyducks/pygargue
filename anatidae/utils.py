from dataclasses import dataclass
from enum import Enum

@dataclass
class UDPConnexion:
    name: str
    addr: str           # remote addr where an UDP server is running
    port: int           # UDP port on wich the bridge is listening
    local_addr: str
    local_port: int     # the port on which this radio will receive data
    rid: str            # the rid associated with this connexion
    allowed: [str]      # which messages can be sent through this radio

