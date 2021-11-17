from dataclasses import dataclass


@dataclass
class Speed:
    vx: float
    vy: float
    vtheta: float


@dataclass
class Pos:
    x: float
    y: float
    theta: float
