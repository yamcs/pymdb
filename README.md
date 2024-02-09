# Yamcs PyMDB

```
pip install yamcs-pymdb
```

Use this Python library to generate XTCE XML files for use with [Yamcs Mission Control](https://yamcs.org):

```python
from yamcs.pymdb import *

spacecraft = System("Spacecraft")

param1 = IntegerParameter(
    system=spacecraft,
    name="param1",
    signed=False,
    encoding=uint8_t,
)

param2 = EnumeratedParameter(
    system=spacecraft,
    name="param2",
    choices=[
        (0, "SUCCESS"),
        (-1, "ERROR"),
    ],
    encoding=int8_t,
)

# Finally, print XTCE
# Emit an XML that conforms to XTCE
print(spacecraft.dumps())
```

## License

LGPL-3.0. See [LICENSE](https://github.com/yamcs/pymdb/blob/master/LICENSE)
