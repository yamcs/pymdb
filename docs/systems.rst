======================
Systems and Subsystems
======================

.. index:: System
.. index:: Subsystem

A ``System`` is the root of a PyMDB model and gives the database its
structure. Every other object — parameter, container, command, algorithm —
belongs to exactly one system. Systems nest through the ``Subsystem`` class,
typically mirroring the physical or functional decomposition of the
spacecraft:

.. code-block:: python

   import yamcs.pymdb as Y

   satellite = Y.System("MySat")

   eps = Y.Subsystem(satellite, "EPS", short_description="Electrical power")
   com = Y.Subsystem(satellite, "COM", short_description="Communications")
   adcs = Y.Subsystem(satellite, "ADCS")

   # Subsystems nest to any depth
   battery = Y.Subsystem(eps, "Battery")

A ``Subsystem`` is a ``System`` in every respect; the only difference is
that it keeps a reference to its parent. Anywhere the manual says "system",
a subsystem works equally.

You can define several independent top-level systems in one script — for
example the spacecraft and the ground support equipment — and export each to
its own XTCE file:

.. code-block:: python

   satellite = Y.System("MySat")
   gse = Y.System("GSE")


Qualified names
===============

.. index:: qualified name
.. index:: DuplicateNameError

Each system defines a namespace. Items are addressed by their *qualified
name*: the slash-separated path from the root system. A parameter
``battery_voltage`` in subsystem ``EPS`` of system ``MySat`` is
``/MySat/EPS/battery_voltage``. These are the names Yamcs displays and that
you use in Yamcs displays, scripts, and APIs.

``System``, ``Parameter``, ``Container``, ``Command`` and ``Algorithm`` all
expose a ``qualified_name`` property, and their ``str()`` form is the
qualified name. A subsystem's ``root`` property returns the top of its tree.

Names must be unique per kind within a system: creating a second parameter
named ``mode`` in the same system raises ``DuplicateNameError``. (A
parameter and a command may share a name, since they are different kinds.)


Descriptive metadata
====================

.. index:: aliases
.. index:: extra

Systems — and nearly every other PyMDB object — accept the same set of
descriptive options:

``short_description``
    A one-line summary, shown in listings in the Yamcs web interface.

``long_description``
    A multi-line description. Yamcs renders this on the item's detail page.

``aliases``
    Alternative names, keyed by namespace, e.g.
    ``aliases={"MDB:OPS Name": "MYSAT_EPS_VBAT"}``. Aliases let other
    systems (displays, procedures, external tools) refer to items by
    mission-specific naming conventions.

``extra``
    Arbitrary key/value information, exported as XTCE ancillary data.
    Yamcs itself ignores unknown keys, but plugins and custom tooling can
    read them.

Since these are the same on every object, the other chapters do not repeat
them.


Navigating the tree
===================

A system exposes its contents through read-only properties and lookup
methods:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Accessor
     - Returns
   * - ``system.parameters``
     - Parameters directly in this system, sorted by qualified name
   * - ``system.containers``
     - Containers directly in this system
   * - ``system.commands``
     - Commands directly in this system
   * - ``system.algorithms``
     - Algorithms directly in this system
   * - ``system.subsystems``
     - Direct child subsystems
   * - ``system.find_parameter(name)``
     - The named parameter; raises ``KeyError`` style lookup error if absent
   * - ``system.find_container(name)`` / ``find_command`` / ``find_algorithm`` / ``find_subsystem``
     - Likewise for the other kinds
   * - ``system.remove_parameter(name)``
     - Removes the named parameter; returns ``False`` if absent
   * - ``system.remove_container(name)`` / ``remove_command`` / ``remove_algorithm`` / ``remove_subsystem``
     - Likewise for the other kinds

All accessors are *direct*: they do not recurse into subsystems. To walk the
whole tree, recurse over ``subsystems`` yourself — a pattern that also
enables model-wide post-processing, see :doc:`large-models`.

Note that ``find_*`` is rarely needed when building a model in one script:
constructors return the object, so you normally just keep the Python
reference. Lookup and removal become useful when the model is assembled
from multiple modules, or when adapting a generated tree afterwards.
