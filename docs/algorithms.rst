==========
Algorithms
==========

.. index:: Algorithm

An algorithm computes values on the ground system: it reads input
parameters, runs a piece of code inside Yamcs, and writes output
parameters. Typical uses are derived engineering values (a power computed
from voltage and current), status roll-ups, and comparisons between
on-board and ground state.

PyMDB only *declares* the algorithm — its code, inputs, outputs and
triggers; execution happens in Yamcs.

.. code-block:: python

   power = Y.FloatParameter(
       system=eps,
       name="power",
       units="W",
       data_source=Y.DataSource.DERIVED,
   )

   Y.Algorithm(
       system=eps,
       name="compute_power",
       language="JavaScript",
       text="power.value = voltage.value * current.value;",
       inputs=[
           Y.InputParameter(voltage, name="voltage", required=True),
           Y.InputParameter(current, name="current", required=True),
       ],
       outputs=[
           Y.OutputParameter(power, name="power"),
       ],
       triggers=[
           Y.ParameterTrigger(voltage),
           Y.ParameterTrigger(current),
       ],
   )

``language`` and ``text`` carry the implementation. Yamcs supports
``JavaScript`` and ``python`` scripts out of the box, as well as
``Java`` (where ``text`` names a Java class on the Yamcs classpath).
Output parameters are usually declared with
``data_source=DataSource.DERIVED``.


Inputs
======

.. index:: InputParameter
.. index:: OutputParameter

``InputParameter`` connects a telemetry parameter to a variable inside the
algorithm:

``parameter``
    The parameter, as a PyMDB object or a qualified name string (for
    parameters outside the PyMDB model).

``name``
    Variable name inside the code. Defaults to the parameter's own name.

``required``
    When ``True``, the algorithm only runs once this input has a value.

``instance``
    Which value to bind: ``0`` (default) is the most recent, negative
    values reach back to earlier samples — ``instance=-1`` gives the
    previous value, allowing delta computations.


Triggers
========

.. index:: ParameterTrigger
.. index:: ContainerTrigger

Triggers state *when* the algorithm runs:

* ``ParameterTrigger(parameter)`` — on each update of the parameter;
* ``ContainerTrigger(container)`` — on each packet matching the container.

Both accept a PyMDB object or a qualified name string, and several
triggers can be combined. An algorithm without triggers only runs when
Yamcs needs its output (for instance while a verifier depends on it).


Java expression algorithms
==========================

.. index:: java-expression

``language="java-expression"`` compiles ``text`` as the body of a Java
method, rather than interpreting it with a scripting engine — faster than
``JavaScript`` or ``python``, at the cost of restricting the algorithm to a
single Java expression/statement:

.. code-block:: python

   Y.Algorithm(
       system=eps,
       name="compute_power_je",
       language="java-expression",
       text=(
           "power.setFloatValue("
           "voltage.getEngValue().getFloatValue() "
           "* current.getEngValue().getFloatValue());"
       ),
       inputs=[
           Y.InputParameter(voltage, name="voltage", required=True),
           Y.InputParameter(current, name="current", required=True),
       ],
       outputs=[
           Y.OutputParameter(power, name="power"),
       ],
   )

Each input and output is bound as an ``org.yamcs.parameter.ParameterValue``,
named as given. Read an input's engineering value with ``getEngValue()``
followed by the accessor matching the parameter's engineering type —
``getFloatValue()``, ``getSint32Value()``, ``getStringValue()``,
``getBooleanValue()``, and so on. Write an output with the corresponding
``set*Value()`` method called directly on it, e.g. ``setFloatValue(...)``
— this sets the engineering value and, if the output has a calibrator,
Yamcs derives the raw value from it.


Inline algorithms
=================

.. index:: UnnamedAlgorithm
.. index:: UnnamedJavaAlgorithm
.. index:: UnnamedJavaScriptAlgorithm

Some places accept a small, unnamed algorithm rather than a reference to a
system-level one:

* custom ``encoder``/``decoder`` on a ``BinaryEncoding``
  (see :doc:`encodings`);
* ``AlgorithmCheck`` in command verifiers (see :doc:`verifiers`).

These use ``UnnamedAlgorithm``, or the shorthands ``UnnamedJavaAlgorithm``
and ``UnnamedJavaScriptAlgorithm``:

.. code-block:: python

   crc_decoder = Y.UnnamedJavaAlgorithm("com.example.yamcs.CrcDecoder")

Unnamed algorithms accept ``inputs`` like regular ones, and ``extra`` for
configuration values the implementation can read. The ready-made decoder
constants listed in :doc:`encodings` (``remaining_binary_decoder`` and
friends) are simply ``UnnamedJavaAlgorithm`` instances pointing at classes
that ship with Yamcs.
