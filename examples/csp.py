from enum import Enum

from yamcs.pymdb import SpaceSystem, csp, dump


class Subsystem(Enum):
    EPS = 0
    COM = 2
    ADCS = 3


class Port(Enum):
    CSP_MGMT = 0
    CSP_PING = 1


spacecraft = SpaceSystem("Spacecraft")
csp_header = csp.add_csp_header(spacecraft, ids=Subsystem, ports=Port)

with open("csp.xml", "wt") as f:
    dump(spacecraft, f)
