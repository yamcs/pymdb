========
Commands
========

.. index:: Command

A ``Command`` describes a telecommand: the arguments an operator fills in,
and the binary packet that Yamcs builds from them. Like parameters,
commands are created with a system and a name:

.. code-block:: python

   set_heater = Y.Command(
       system=eps,
       name="SetHeater",
       short_description="Switch a battery heater",
       arguments=[
           Y.IntegerArgument(name="heater_id", signed=False,
                             minimum=1, maximum=4, encoding=Y.uint8_t),
           Y.BooleanArgument(name="status", encoding=Y.uint8_t),
       ],
   )

When no explicit layout is given, the encoded command consists of the
arguments one after the other, in declaration order (arguments without an
encoding are skipped). Sections below cover explicit layouts and command
hierarchies, which is how real packet formats are usually modelled.


Arguments
=========

.. index:: Argument

Argument classes parallel the parameter classes: ``IntegerArgument``,
``FloatArgument``, ``EnumeratedArgument``, ``BooleanArgument``,
``StringArgument``, ``BinaryArgument``, ``AbsoluteTimeArgument``,
``AggregateArgument`` and ``ArrayArgument``. They accept the same
type-specific options as their parameter counterparts — ``choices``,
``bits``, ``signed``, ``minimum``/``maximum``, ``min_length``/
``max_length``, ``units``, ``calibrator``, ``encoding`` — with two
differences:

* Arguments belong to a command, not a system: they are constructed
  standalone and passed via the command's ``arguments`` list.
* Instead of ``initial_value`` they take ``default``, the value prefilled
  when issuing the command.

Validity ranges (``minimum``/``maximum``) are enforced by Yamcs when the
command is issued, so encode your safety limits here. For arguments with a
``calibrator``, the operator provides the engineering value and Yamcs
de-calibrates it before encoding.


Command entries
===============

.. index:: ArgumentEntry
.. index:: FixedValueEntry

For explicit control over the packet layout, pass ``entries``. Three entry
types can be mixed:

``ArgumentEntry(argument)``
    Encodes an argument's value.

``FixedValueEntry(binary, name=None, bits=None)``
    Encodes a constant, given as ``bytes`` or as a hex string
    (``"DEADBEEF"``). With ``bits`` set, the value is left-padded with
    zeros or truncated (most-significant bits dropped) to that size —
    convenient for sub-byte fields.

``ParameterEntry(parameter)``
    Encodes the current value of a telemetry parameter into the command.

All entry types support the same positioning options as container entries
(``bitpos``, ``offset``) and a ``condition`` expression that includes the
entry only when it holds — see :doc:`containers` and :doc:`expressions`.

.. code-block:: python

   payload = Y.BinaryArgument(name="payload", encoding=Y.BinaryEncoding())

   ping = Y.Command(
       system=obc,
       name="Ping",
       arguments=[payload],
       entries=[
           Y.FixedValueEntry(name="magic", binary="1ACF"),
           Y.FixedValueEntry(name="command_id", binary="0004"),
           Y.ArgumentEntry(payload),
       ],
   )

Fields like sequence counts or checksums that the ground system fills in
during link post-processing are typically modelled as zeroed
``FixedValueEntry`` items, as the CCSDS helper does — see :doc:`headers`.


Command hierarchies
===================

.. index:: abstract command
.. index:: assignments

Command sets usually share a common header: every command of a subsystem
starts with the same fields, differing only in an ID field and the
payload. This is modelled with inheritance, like containers:

* ``abstract=True`` marks a command that cannot be sent itself and only
  serves as a base;
* ``base`` points to the parent command (or names it as a string);
* ``assignments`` pins arguments *of the base* to concrete values in the
  derived command, keyed by argument name.

.. code-block:: python

   command_id = Y.IntegerArgument(name="command_id", signed=False,
                                  encoding=Y.uint16_t)

   # The abstract header: an id field, filled in per command
   header = Y.Command(
       system=obc,
       name="Header",
       abstract=True,
       arguments=[command_id],
   )

   reboot = Y.Command(
       system=obc,
       name="Reboot",
       base=header,
       assignments={command_id.name: 1},
   )

   set_mode = Y.Command(
       system=obc,
       name="SetMode",
       base=header,
       assignments={command_id.name: 2},
       arguments=[
           Y.EnumeratedArgument(name="mode", choices=Mode, encoding=Y.uint8_t),
       ],
   )

A derived command's entries follow the base's entries. The operator only
sees the remaining free arguments — for ``Reboot``, none at all.
``get_argument(name)`` looks an argument up by name, searching base
commands too.


Significance
============

.. index:: CommandLevel

``level`` declares how consequential a command is, using the levels of
ISO 14950; Yamcs uses this to require confirmation or elevated privileges
before issuing:

.. list-table::
   :widths: 25 75

   * - ``NORMAL``
     - Level D. Regular operations — the default.
   * - ``VITAL``
     - Level C. Not critical, but essential to mission success; wrongly
       timed, could cause momentary loss of the mission.
   * - ``CRITICAL``
     - Level B. Wrongly timed or in the wrong configuration, could cause
       irreversible loss or damage.
   * - ``FORBIDDEN``
     - Level A. Reserved for unforeseen contingencies; could cause
       irreversible damage.

``warning_message`` supplies the text shown to the operator when
confirmation is requested:

.. code-block:: python

   Y.Command(
       system=obc,
       name="FormatFlash",
       level=Y.CommandLevel.CRITICAL,
       warning_message="Erases all stored telemetry. Confirm downlink is complete.",
   )


Transmission constraints
========================

.. index:: TransmissionConstraint

A ``TransmissionConstraint`` holds a command back until a condition on
current telemetry is satisfied:

.. code-block:: python

   Y.Command(
       system=eps,
       name="DeployAntenna",
       constraint=Y.TransmissionConstraint(
           expression=Y.eq(mode, "NOMINAL"),
           timeout=30,   # wait up to 30 s for the condition
       ),
   )

With ``timeout=0`` (the default) the constraint is checked once and the
command fails immediately if it does not hold. A command may carry several
constraints (pass a list); all must be satisfied, and constraints inherited
from ``base`` commands are checked as well.

What happens *after* transmission — confirming the command was received,
executed, completed — is the subject of :doc:`verifiers`.
