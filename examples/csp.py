from enum import Enum

import yamcs.pymdb as Y
from yamcs.pymdb import csp


class Subsystem(Enum):
    EPS = 0
    COM = 2
    ADCS = 3


spacecraft = Y.System("Spacecraft")
csp_header = csp.add_csp_header(spacecraft, ids=Subsystem)

with open("csp.xml", "wt") as f:
    spacecraft.dump(f)
