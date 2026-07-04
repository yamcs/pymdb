===============
Getting Started
===============

This chapter builds a small but complete mission database — one packet, one
command — and loads it into Yamcs.


Installation
============

PyMDB requires Python 3.9 or later:

.. code-block:: text

   pip install --upgrade yamcs-pymdb

The library is only needed on the machine where you generate the XML,
never on the Yamcs server itself.


A first model
=============

Create a file ``mymdb.py``:

.. code-block:: python
   :caption: mymdb.py

   from yamcs.pymdb import *

   spacecraft = System("Spacecraft")

   # Two telemetry parameters, with their on-wire encoding
   mode = EnumeratedParameter(
       system=spacecraft,
       name="mode",
       choices=[(0, "OFF"), (1, "SAFE"), (2, "NOMINAL")],
       encoding=uint8_t,
   )
   voltage = FloatParameter(
       system=spacecraft,
       name="battery_voltage",
       units="V",
       encoding=float32_t,
   )

   # A telemetry packet carrying both parameters, in order
   hk_packet = Container(
       system=spacecraft,
       name="hk_packet",
       short_description="Housekeeping",
       entries=[
           ParameterEntry(mode),
           ParameterEntry(voltage),
       ],
   )

   # A command with one argument
   set_mode = Command(
       system=spacecraft,
       name="SetMode",
       arguments=[
           EnumeratedArgument(
               name="mode",
               choices=[(0, "OFF"), (1, "SAFE"), (2, "NOMINAL")],
               encoding=uint8_t,
           ),
       ],
   )

   with open("mymdb.xml", "wt") as f:
       spacecraft.dump(f)

Run it:

.. code-block:: text

   python mymdb.py

The script writes ``mymdb.xml``, an XTCE file describing the system
``/Spacecraft`` with its two parameters, one container and one command.
That file — not the Python script — is what Yamcs consumes.

The example already shows the pattern used throughout PyMDB: objects are
constructed with keyword arguments, and passing the ``system`` registers
them into the tree. There is nothing else to call; the model *is* the set
of objects you created.


Loading into Yamcs
==================

Reference the generated file in the ``mdb`` section of your Yamcs instance
configuration:

.. code-block:: yaml
   :caption: etc/yamcs.myinstance.yaml

   mdb:
     - type: xtce
       args:
         file: mdb/mymdb.xml

After each change to the Python model, regenerate the XML and restart
Yamcs. Many projects add the generation step to their build, so the XML in
the deployment is always derived from the Python source.


Import styles
=============

The example above uses a star import, which is convenient for small models:
everything in the library is available under a flat namespace. Larger
projects usually prefer an alias instead:

.. code-block:: python

   import yamcs.pymdb as Y

   spacecraft = Y.System("Spacecraft")
   voltage = Y.FloatParameter(spacecraft, "battery_voltage", encoding=Y.float32_t)

Both styles refer to the same names; ``yamcs.pymdb`` re-exports the entire
public API at the top level. The alias's main benefit is discoverability:
typing ``Y.`` and letting the IDE's autocompletion list what follows is a
faster way to find the right class than recalling it from a flat,
star-imported namespace. The rest of this manual uses the ``Y.`` alias
convention in longer examples, and plain names in short fragments.


Where to go next
================

* :doc:`systems` — structuring the model as a tree of (sub)systems.
* :doc:`parameters` and :doc:`encodings` — the full range of telemetry
  types and their binary representations.
* :doc:`containers` — packet layouts, including packet identification.
* :doc:`commands` — command hierarchies, argument types, verification.
* :doc:`large-models` — patterns for databases with thousands of
  parameters.
