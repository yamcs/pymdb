==========
Parameters
==========

.. index:: Parameter

A parameter is a single telemetry value: a voltage, a mode, a counter, a
timestamp. In PyMDB you pick the parameter class matching the *engineering
type* — what users should see — and construct it with a system and a name:

.. code-block:: python

   temperature = Y.FloatParameter(
       system=eps,
       name="battery_temp",
       units="degC",
       short_description="Battery pack temperature",
       encoding=Y.int16_t,
       calibrator=Y.Polynomial([0.0, 0.01]),
   )

There are nine parameter classes, one per engineering type:

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Class
     - Engineering value
     - Example
   * - ``IntegerParameter``
     - Integer
     - packet counter
   * - ``FloatParameter``
     - 32- or 64-bit decimal
     - voltage
   * - ``EnumeratedParameter``
     - One state out of a discrete set
     - mode
   * - ``BooleanParameter``
     - Two-state value
     - switch status
   * - ``StringParameter``
     - Character string
     - software version
   * - ``BinaryParameter``
     - Byte block
     - opaque payload
   * - ``AbsoluteTimeParameter``
     - Instant in time
     - onboard time
   * - ``AggregateParameter``
     - Structure of named members
     - packet header
   * - ``ArrayParameter``
     - Array of another data type
     - thermistor readings

The engineering type is only half the story: to appear in a telemetry
packet, a parameter also needs an ``encoding`` describing its raw binary
form. Encodings have their own chapter, :doc:`encodings`. Parameters
without an encoding are fine too — typical for values produced by
:doc:`algorithms <algorithms>` or set from ground software.


Common options
==============

All parameter classes share these constructor options (besides the
descriptive metadata from :doc:`systems`):

.. index:: DataSource

``data_source``
    Where values come from. One of:

    .. list-table::
       :widths: 30 70

       * - ``DataSource.TELEMETERED``
         - Received in telemetry — the default.
       * - ``DataSource.DERIVED``
         - Calculated, usually by an algorithm.
       * - ``DataSource.CONSTANT``
         - A constant of the system, e.g. a vehicle ID.
       * - ``DataSource.LOCAL``
         - Set by ground software, e.g. via the Yamcs API.
       * - ``DataSource.GROUND``
         - Produced by a ground asset other than the spacecraft, e.g. a
           ground station receiver.

``initial_value``
    The value the parameter holds before any update arrives. The Python
    type follows the engineering type: ``int``, ``float``, ``str`` (or
    enum label), ``bool``, ``bytes``, ``datetime``, a ``dict`` for
    aggregates, a list for arrays.

``persistent``
    When ``True`` (the default), Yamcs saves the last value across
    restarts. With both ``persistent`` and ``initial_value`` set, the
    initial value is only used when there is no persisted value yet.

``units``
    Engineering units as a free-text string (``"V"``, ``"degC"``, ...),
    shown alongside values in the Yamcs interfaces.


Numbers: integers and floats
============================

.. index:: IntegerParameter
.. index:: FloatParameter

``IntegerParameter`` takes ``signed`` (default ``True``) and ``bits``
(default 32) for the engineering type, plus an optional validity range:

.. code-block:: python

   Y.IntegerParameter(
       system=obc,
       name="reboot_count",
       signed=False,
       minimum=0,
       maximum=1000,
       encoding=Y.uint16_t,
   )

``FloatParameter`` takes ``bits`` (32 or 64) and a validity range where each
bound can be made exclusive (``minimum_inclusive=False``,
``maximum_inclusive=False``).

The range describes *valid* engineering values; Yamcs flags values outside
it as out-of-limits. For operational alarm thresholds (watch, warning,
critical, ...) see :doc:`alarms` — both numeric parameter classes accept
``alarm`` and ``context_alarms`` options.

Numeric parameters (and members/arguments) also accept a ``calibrator``
that converts the raw count to the engineering value — see
:doc:`calibrators`.

.. note::

   A common mistake is a 32-bit float engineering type with a 64-bit
   encoding, which loses precision. The check function
   ``checks.check_float_encoding`` detects this — see :doc:`generating`.


Enumerations and booleans
=========================

.. index:: Choices
.. index:: EnumeratedParameter
.. index:: BooleanParameter

``EnumeratedParameter`` maps integer values to state labels. The ``choices``
option accepts either a sequence of tuples — ``(value, label)`` or
``(value, label, description)`` — or a Python :class:`enum.Enum` class:

.. code-block:: python

   import enum

   class Mode(enum.Enum):
       OFF = 0
       SAFE = 1
       NOMINAL = 2

   Y.EnumeratedParameter(obc, "mode", choices=Mode, encoding=Y.uint8_t)

   # equivalent, with per-state descriptions possible:
   Y.EnumeratedParameter(
       obc,
       "mode2",
       choices=[(0, "OFF"), (1, "SAFE"), (2, "NOMINAL", "Regular operations")],
       encoding=Y.uint8_t,
   )

Enumerated parameters accept an ``EnumerationAlarm`` (and context alarms)
to raise alerts on specific states — see :doc:`alarms`.

``BooleanParameter`` is a two-state enumeration where 0 and 1 map to
configurable labels via ``zero_string_value`` (default ``"False"``) and
``one_string_value`` (default ``"True"``):

.. code-block:: python

   Y.BooleanParameter(
       eps,
       "heater_status",
       zero_string_value="OFF",
       one_string_value="ON",
       encoding=Y.uint1_t,
   )


Strings and binary
==================

.. index:: StringParameter
.. index:: BinaryParameter

``StringParameter`` and ``BinaryParameter`` optionally restrict the
engineering value's size with ``min_length`` and ``max_length`` (characters
for strings, bytes for binary). How the size is determined on the wire —
fixed, length-prefixed, or terminator-based — is a property of the
encoding, see :doc:`encodings`.


Time parameters
===============

.. index:: Epoch
.. index:: AbsoluteTimeParameter

``AbsoluteTimeParameter`` represents an instant in time. It requires a
``reference`` that anchors the raw count:

* an ``Epoch`` constant: ``Epoch.GPS``, ``Epoch.TAI``, ``Epoch.J2000`` or
  ``Epoch.UNIX``;
* a specific ``datetime``, for mission-defined epochs;
* another ``AbsoluteTimeParameter``, for times expressed relative to a
  dynamic reference.

.. code-block:: python

   Y.AbsoluteTimeParameter(
       system=obc,
       name="coarse_time",
       reference=Y.Epoch.GPS,
       encoding=Y.IntegerTimeEncoding(bits=32),
   )

The scale and offset of the raw count are set on the time encoding — see
:doc:`encodings`.


Aggregates: structured values
=============================

.. index:: AggregateParameter
.. index:: Member

``AggregateParameter`` groups related values into one parameter with named
*members*, comparable to a C struct. Members are built from the ``Member``
family of classes, which mirrors the parameter classes:
``IntegerMember``, ``FloatMember``, ``EnumeratedMember``, ``BooleanMember``,
``StringMember``, ``BinaryMember``, ``AbsoluteTimeMember`` — and
``AggregateMember`` / ``ArrayMember`` for nesting.

.. code-block:: python

   packet_id = Y.AggregateParameter(
       system=spacecraft,
       name="ccsds_packet_id",
       members=[
           Y.IntegerMember(name="version", signed=False, encoding=Y.uint3_t),
           Y.BooleanMember(name="secondary_header", encoding=Y.uint1_t),
           Y.IntegerMember(name="apid", signed=False, encoding=Y.uint11_t),
       ],
   )

Each member takes the same type-specific options as its parameter
counterpart (``choices``, ``bits``, ``calibrator``, ...) plus its own
``encoding`` and an optional ``initial_value``. The aggregate itself does
not have an encoding: when placed in a container, its members are encoded
one after the other.

In Yamcs, members are addressed with dotted names, e.g.
``ccsds_packet_id.apid``. Inside a PyMDB model — for instance in an
:doc:`expression <expressions>` — a member is referenced with
``ParameterMember``:

.. code-block:: python

   apid = Y.ParameterMember(packet_id, path=apid_member)

where ``path`` can be a single member or a list of members for nested
aggregates.


Arrays
======

.. index:: ArrayParameter
.. index:: ParameterValue

``ArrayParameter`` repeats a single data type a number of times. The
element type is given as a *data type* object — one of the ``*DataType``
classes, carrying the same type-specific options as the corresponding
parameter class:

.. code-block:: python

   converter_voltages = Y.ArrayParameter(
       system=eps,
       name="converter_voltages",
       short_description="Voltage of MPPT converters",
       data_type=Y.IntegerDataType(signed=False, units="mV",
                                   encoding=Y.uint16le_t),
       length=4,
   )

``length`` may be:

* an ``int`` — a fixed-size array;
* ``ParameterValue(other_parameter)`` — a dynamic size, read at extraction
  time from another parameter (typically a count field earlier in the same
  packet). The parameter can also be given by name (string) when it is not
  managed with PyMDB.

.. code-block:: python

   count = Y.IntegerParameter(eps, "sample_count", signed=False,
                              encoding=Y.uint8_t)
   samples = Y.ArrayParameter(
       system=eps,
       name="samples",
       data_type=Y.FloatDataType(encoding=Y.float32_t),
       length=Y.ParameterValue(count),
   )
