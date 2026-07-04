========================
Structuring Large Models
========================

A mission database quickly grows to hundreds or thousands of parameters.
Written naively — one flat script, one constructor call per parameter with
every option spelled out — the Python source becomes as unwieldy as the
XML it replaces. This chapter collects patterns from real projects that
keep large models readable. They are all plain Python; PyMDB requires none
of them, but its object model is designed to make them work.


One module per subsystem
========================

The natural first cut is to mirror the system tree in the source layout:
a package with one module (or sub-package) per subsystem, and a top-level
script that assembles and exports the tree.

.. code-block:: text

   mdb/
     mymdb.py        <- assembles the tree, dumps XML
     sat/
       __init__.py   <- the Satellite system class
       eps.py
       com.py
       adcs.py

Each module defines its part of the tree, taking the parent system as an
argument:

.. code-block:: python
   :caption: sat/eps.py

   import yamcs.pymdb as Y

   def add_eps(parent: Y.System) -> Y.Subsystem:
       eps = Y.Subsystem(parent, "EPS", short_description="Electrical power")

       Y.FloatParameter(eps, "battery_voltage", units="V", encoding=Y.uint12_t)
       # ... more parameters, containers, commands

       return eps

.. code-block:: python
   :caption: mymdb.py

   import yamcs.pymdb as Y
   from sat.eps import add_eps
   from sat.com import add_com

   satellite = Y.System("MySat")
   add_eps(satellite)
   add_com(satellite)

   with open("mysat.xml", "wt") as f:
       satellite.dump(f)

Because objects register themselves into their system on construction,
modules do not need to return or collect anything — though returning the
subsystem (or specific parameters other modules need) makes cross
references explicit.


One XTCE file per subsystem
============================

.. index:: subLoaders

The pattern above still assembles the whole tree in Python and exports it
as a single XTCE file. Yamcs does not require that: its ``mdb`` loader
configuration can itself express a tree, via ``subLoaders``, where each
loader's output is grafted onto its parent as a nested subsystem:

.. code-block:: yaml
   :caption: etc/yamcs.myinstance.yaml

   mdb:
     - type: xtce
       args:
         file: mdb/mysat.xml
       subLoaders:
         - type: xtce
           args:
             file: mdb/eps.xml
         - type: xtce
           args:
             file: mdb/com.xml

PyMDB mirrors this by dumping each subsystem to its own file, passing
``skip_subsystems=True`` where a file's own subsystems are exported
separately rather than nested inline:

.. code-block:: python

   with open("mysat.xml", "wt") as f:
       satellite.dump(f, skip_subsystems=True)

   with open("eps.xml", "wt") as f:
       eps.dump(f)

   with open("com.xml", "wt") as f:
       com.dump(f)

References across subsystems still work: PyMDB emits them as XTCE relative
paths (``../mode``, and so on), which resolve correctly once Yamcs
reassembles the files — *provided* the ``subLoaders`` tree mirrors the
Python nesting exactly, level for level.

This is mainly worth it for very large models, where regenerating and
reloading a single subsystem's file is faster than the whole tree, or
where different teams own different subsystem files. For most projects,
the single-file export from the previous section is simpler and enough.


Subclassing System and Subsystem
================================

Where subsystems share structure — several instances of the same device
type, a common command header, a standard set of housekeeping packets —
subclassing takes the pattern further. The constructor builds the shared
content; per-instance details arrive as arguments:

.. code-block:: python

   class DeviceSubsystem(Y.Subsystem):
       """A device on the bus, with the standard housekeeping packet."""

       def __init__(self, parent: Y.System, name: str, device_id: int):
           super().__init__(parent, name)

           self.device_id = device_id
           self.temperature = Y.FloatParameter(
               self, "temperature", units="degC", encoding=Y.int16_t
           )
           self.hk = Y.Container(
               self, "hk",
               base=parent.find_container("header"),
               condition=Y.eq(parent.find_parameter("device_id"), device_id),
               entries=[Y.ParameterEntry(self.temperature)],
           )

   sensor_a = DeviceSubsystem(satellite, "SensorA", device_id=1)
   sensor_b = DeviceSubsystem(satellite, "SensorB", device_id=2)

When a fleet of identical units is involved, instantiation becomes a loop:

.. code-block:: python

   for device_id, name in [(1, "SensorA"), (2, "SensorB"), (3, "SensorC")]:
       DeviceSubsystem(satellite, name, device_id=device_id)

Storing the created objects as attributes (``self.temperature``) gives the
rest of the model a typed, discoverable handle — no string lookups needed.
The same technique applies to the root: a ``Satellite(Y.System)`` subclass
can install the CCSDS or CSP header (:doc:`headers`) and expose it as an
attribute for all subsystems to build on.

Two small idioms round this off. A subsystem class's docstring can double
as its MDB description::

   if self.__class__.__doc__:
       self.long_description = dedent(self.__class__.__doc__).lstrip()

And objects returned by helpers remain plain attributes that can be
adjusted after the fact — for instance filling in the address enumeration
of the CSP header once the node list is known:

.. code-block:: python

   self.csp_header = Y.csp.add_csp_header(self)
   self.csp_header.tc_src.choices = csp_ids
   self.csp_header.tm_src.choices = csp_ids


Helpers that build closed loops
===============================

Helper methods need not stop at single parameters. Devices with a
request/reply protocol (see :doc:`verifiers`) involve three coupled
objects per interaction — the command, the reply container, and the
verifier connecting them — plus shared discriminator values such as a
command ID. A pair of helper methods keeps them consistent:

.. code-block:: python

   class Service(Y.Subsystem):
       """One request/reply service of a device, on a fixed port."""

       def __init__(self, device: DeviceSubsystem, name: str, port: int):
           super().__init__(device, name)
           self.device = device
           # Abstract bases for this service: port pinned once
           self.request = Y.Command(
               self, "Request", abstract=True,
               base=device.request_command,
               assignments={device.dport.name: port},
           )
           self.reply = Y.Container(
               self, "Reply", abstract=True,
               base=device.reply_container,
               condition=Y.eq(device.sport, port),
           )

       def add_request(self, command_id, name, arguments=None):
           return Y.Command(
               self, name,
               base=self.request,
               assignments={self.device.command_id.name: command_id},
               arguments=arguments,
           )

       def add_reply(self, request, parameters):
           command_id = request.assignments["command_id"]
           reply = Y.Container(
               self, f"{request.name}Reply",
               base=self.reply,
               condition=Y.eq(self.device.reply_command_id, command_id),
               entries=[Y.ParameterEntry(p) for p in parameters],
           )
           request.complete_verifiers.append(
               Y.CompleteVerifier(check=Y.ContainerCheck(reply), timeout=5)
           )
           return reply

Each service interaction is then a few declarative lines:

.. code-block:: python

   get_time = service.add_request(0, "GetTime")
   service.add_reply(get_time, parameters=[error_code, timestamp])

Recurring verifier configurations can equally be captured by subclassing —
a ``CompleteVerifier`` subclass whose constructor assembles the check
(perhaps an ``AlgorithmCheck`` with its inputs and ``extra``
configuration) from just the reply container.


Helper methods for recurring types
==================================

Most projects use a handful of parameter shapes over and over — the same
encoding, termination, unit conventions. Rather than repeating five
options at every call site, add helper methods to your subsystem class
that fix the common choices and expose only what varies:

.. code-block:: python

   class MissionSubsystem(Y.Subsystem):

       def add_float(self, name, units=None, description=None,
                     calibrator=None, alarm=None):
           return Y.FloatParameter(
               system=self,
               name=name,
               short_description=description,
               units=units,
               bits=32,
               encoding=Y.float32le_t,
               calibrator=calibrator,
               alarm=alarm,
           )

       def add_uint(self, name, units=None, description=None, bits=32):
           return Y.IntegerParameter(
               system=self,
               name=name,
               short_description=description,
               units=units,
               signed=False,
               bits=bits,
               encoding=Y.IntegerEncoding(bits=bits, little_endian=True),
           )

Parameter definitions then shrink to one line each, and a mission-wide
encoding decision (say, switching endianness) is a one-place change:

.. code-block:: python

   eps.add_float("battery_voltage", units="V", description="Main bus voltage")
   eps.add_uint("reboot_count", description="Reboots since launch", bits=16)


Generating definitions from data
================================

When parameter lists already exist elsewhere — an ICD spreadsheet, a CSV
export from the manufacturer — loop over the data instead of transcribing
it:

.. code-block:: python

   import csv

   with open("eps_telemetry.csv", newline="") as f:
       entries = []
       for row in csv.DictReader(f):
           p = eps.add_float(row["name"], units=row["units"],
                             description=row["description"])
           entries.append(Y.ParameterEntry(p))

   Y.Container(eps, "hk", entries=entries)

This keeps the authoritative source authoritative, and the Python layer
becomes a (reviewable, versioned) transformation.


Post-processing the tree
========================

Because the model stays a live object tree until export, cross-cutting
adjustments can run as a final pass, instead of being threaded through
every definition. Walking the tree is a few lines:

.. code-block:: python

   def add_ops_names(system: Y.System):
       """Give every parameter an OPS name alias derived from its path."""
       for parameter in system.parameters:
           ops_name = parameter.qualified_name[1:].replace("/", "_").upper()
           parameter.aliases["MDB:OPS Name"] = ops_name
       for subsystem in system.subsystems:
           add_ops_names(subsystem)

   add_ops_names(satellite)

The ``find_*`` and ``remove_*`` accessors (:doc:`systems`) support more
surgical rewrites — replacing a parameter with a different definition, or
adapting a subsystem you imported from a shared library but need to tweak
for one mission.
