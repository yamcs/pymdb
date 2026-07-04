===============
Generating XTCE
===============

.. index:: XTCE
.. index:: dump

Once the tree is built, each top-level system exports itself with
``dump()`` (to a file-like object) or ``dumps()`` (to a string):

.. code-block:: python

   with open("mysat.xml", "wt") as f:
       satellite.dump(f)

   xml = satellite.dumps()

Every top-level system produces one XTCE file; a model with a spacecraft
system and a GSE system is exported as two files.


Export options
==============

Both methods accept the same keyword-only options:

``format``
    ``"xtce-1.2"`` (the default, natively supported by Yamcs) or
    ``"xtce-1.3"``.

``indent``
    Indentation string per level, default two spaces. Use ``""`` for the
    most compact output.

``top_comment``
    The XML comment inserted at the top of the file. By default this is a
    notice that the file is generated; pass a string to customize it, or
    ``False`` to omit it.

``skip_parameters``, ``skip_containers``, ``skip_commands``, ``skip_algorithms``, ``skip_subsystems``
    Leave the corresponding sections out of the export. Useful for
    partial exports, e.g. producing a telemetry-only file.

If the model contains something that cannot be represented in the chosen
format, the export raises ``ExportError`` with a message naming the
offending item. Since generation walks the entire tree, running the export
is also the quickest overall sanity check of a model.


Loading into Yamcs
==================

Reference the generated file(s) from the ``mdb`` section of the Yamcs
instance configuration:

.. code-block:: yaml
   :caption: etc/yamcs.myinstance.yaml

   mdb:
     - type: xtce
       args:
         file: mdb/mysat.xml
     - type: xtce
       args:
         file: mdb/gse.xml

Yamcs reads the file at startup: after regenerating, restart Yamcs (or the
instance) to pick up the changes.


Validation checks
=================

.. index:: checks

The ``yamcs.pymdb.checks`` module offers read-only sanity checks to run
over a finished model, before or alongside the export. Each function
walks the full tree, prints a line per finding, and returns ``True`` when
all is well — convenient for turning into a build failure:

.. code-block:: python

   from yamcs.pymdb import checks

   ok = checks.check_complete_verifiers(satellite)
   ok &= checks.check_float_encoding(satellite)
   assert ok, "MDB validation failed"

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Verifies that...
   * - ``check_complete_verifiers``
     - every non-abstract command has a verifier able to complete it
       successfully (see :doc:`verifiers`)
   * - ``check_float_encoding``
     - no 32-bit float parameter/argument uses a 64-bit encoding (a
       common precision bug)
   * - ``check_little_endian_only``
     - all multi-byte integer encodings are little endian — for projects
       whose hardware is uniformly little endian, this catches a
       forgotten ``le`` variant

These checks are optional helpers, not part of the export; a model that
fails them still exports fine.


Errors
======

.. index:: ExportError
.. index:: DuplicateNameError
.. index:: SizeCalculationError

The library raises three exception types of its own:

.. list-table::
   :widths: 35 65

   * - ``ExportError``
     - The model cannot be represented in the requested XTCE format.
   * - ``DuplicateNameError``
     - An object was created with a name already used by a sibling of the
       same kind (see :doc:`systems`).
   * - ``SizeCalculationError``
     - A fixed bit size could not be determined, e.g.
       ``Container.fit_entries()`` over a dynamically sized entry.
