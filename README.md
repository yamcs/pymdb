# Yamcs PyMDB

```
pip install yamcs-pymdb
```

Use this Python library to generate XTCE XML files for use with [Yamcs Mission Control](https://yamcs.org):

```python
from yamcs.pymdb import *

spacecraft = SpaceSystem("Spacecraft")

param1 = spacecraft.add_integer_parameter(
    name="param1",
    signed=False,
    encoding=uint8_t,
)

param2 = spacecraft.add_enumerated_parameter(
    name="param2",
    choices=[
        (0, "SUCCESS"),
        (-1, "ERROR"),
    ],
    encoding=int8_t,
)

# Finally, print XTCE
# Emit an XML that conforms to XTCE
print(dumps(spacecraft))
```
