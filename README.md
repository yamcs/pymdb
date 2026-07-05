# Yamcs PyMDB

```
pip install yamcs-pymdb
```

Use this Python library to generate XTCE XML files for use with [Yamcs Mission Control](https://yamcs.org):

```python
import yamcs.pymdb as Y

spacecraft = Y.System("Spacecraft")

param1 = Y.IntegerParameter(
    system=spacecraft,
    name="param1",
    signed=False,
    encoding=Y.uint8_t,
)

param2 = Y.EnumeratedParameter(
    system=spacecraft,
    name="param2",
    choices=[
        (0, "SUCCESS"),
        (-1, "ERROR"),
    ],
    encoding=Y.int8_t,
)

# Emit an XML that conforms to XTCE
print(spacecraft.dumps())
```

## License

LGPL-3.0. See [LICENSE](https://github.com/yamcs/pymdb/blob/master/LICENSE)
