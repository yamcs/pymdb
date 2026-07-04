============
Introduction
============

A Yamcs Mission Database describes everything Yamcs needs to know about the
system it monitors and commands: which telemetry parameters exist, how they
are packed into packets, how raw counts convert to engineering values, when
to raise alarms, which telecommands can be sent and how their execution is
verified.

PyMDB lets you write this description in Python. You build a tree of plain
Python objects — systems, parameters, containers, commands — and then export
the whole tree as an XTCE XML file. Yamcs loads that file natively; PyMDB
itself is not needed at runtime and does not talk to Yamcs.

.. figure:: _images/pipeline.*
   :alt: model.py is run to produce mdb.xml, which Yamcs loads at startup.

Because the model is a Python program, you get the tools of a programming
language for free: loops for repetitive definitions, functions and classes
for shared structure, imports for splitting a large database across files,
and meaningful diffs in version control. :doc:`large-models` shows how real
projects use this.


The object model
================

Everything in PyMDB is created by constructing objects. There is no separate
builder or registration API: constructing a parameter with a reference to
its system is what adds it to the model.

* A :doc:`System <systems>` is a named container and forms the root of the
  tree. ``Subsystem`` nests systems to any depth, mirroring the structure of
  the spacecraft or device.
* :doc:`Parameters <parameters>` are the telemetry values: integers, floats,
  enumerations, strings, times, and structured types.
* :doc:`Containers <containers>` describe telemetry packets: which
  parameters appear where in the binary packet.
* :doc:`Commands <commands>` describe telecommands: their arguments, their
  binary layout, and (via :doc:`verifiers <verifiers>`) how Yamcs confirms
  their execution.
* :doc:`Algorithms <algorithms>` compute derived parameters on board the
  ground system, from other parameters.

Once the tree is built, a single call generates the XTCE file — see
:doc:`generating`.


Engineering values and raw values
=================================

One distinction runs through the whole library and is worth internalizing
early: the difference between a value's *engineering* form and its *raw*
form.

The **engineering value** is what users see and scripts work with: a battery
voltage of ``12.7`` (a float), a mode called ``"SAFE"`` (an enumeration
state). In PyMDB, the choice of parameter class — ``FloatParameter``,
``EnumeratedParameter``, ... — defines the engineering type.

The **raw value** is how the same quantity travels over the wire: perhaps an
unsigned 12-bit integer count, or a single byte holding a mode number. In
PyMDB this is described by an :doc:`encoding <encodings>` object, passed to
the parameter via its ``encoding`` argument.

The two are connected by an optional :doc:`calibrator <calibrators>`, which
converts raw counts into engineering units.

.. code-block:: python

   voltage = FloatParameter(
       system=eps,
       name="battery_voltage",
       units="V",
       encoding=uint12_t,                      # raw: 12-bit unsigned integer
       calibrator=Polynomial([0.0, 0.0044]),   # eng = 0.0044 * raw
   )

A parameter without an encoding is perfectly valid — for example a value
computed by an algorithm, or set from ground software — but only parameters
with an encoding can appear in telemetry packets or be encoded into
commands.


Relation to XTCE
================

XTCE (XML Telemetric and Command Exchange) is the OMG/CCSDS standard format
that Yamcs uses for mission databases. PyMDB is deliberately close to XTCE
concepts — systems map to ``SpaceSystem`` elements, containers to
``SequenceContainer``, and so on — but you do not need to know XTCE to use
it. Where XTCE requires verbose structures (parameter types separate from
parameters, for instance), PyMDB folds them into a single Python object and
generates the required XML on export.

PyMDB can generate XTCE 1.2 (the default) as well as the newer XTCE 1.3.
Yamcs understands both, but 1.2 remains the default here since 1.3 is not
yet as widely adopted.
