# Yamcs PyMDB

> [!WARNING]
> This software is in beta development status. Documentation is limited, and API is subject to change.
>
> If you'd like to try it out, have a look at the [examples](https://github.com/yamcs/pymdb/tree/master/examples) which explain the base setup for either CCSDS or CSP-style packets. Other common formats will be added over time.

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

# Emit an XML that conforms to XTCE
print(spacecraft.dumps())
```

## License

LGPL-3.0. See [LICENSE](https://github.com/yamcs/pymdb/blob/master/LICENSE)
