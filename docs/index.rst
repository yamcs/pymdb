===========
Yamcs PyMDB
===========

.. raw:: latex

   \chapter*{About}

Yamcs PyMDB is a Python library for writing the Mission Database (MDB) of a
`Yamcs <https://yamcs.org>`_ deployment. Instead of editing XML by hand or
maintaining spreadsheets, you describe parameters, packets, commands, alarms
and algorithms as plain Python objects, and PyMDB generates the equivalent
XTCE file that Yamcs loads.

This guide introduces the concepts step by step, and doubles as a reference:
every feature of the library is covered in one of the chapters, and the
appendix lists all public names with a pointer to the chapter that describes
them.

.. toctree::
    :maxdepth: 1
    :titlesonly:

    introduction
    getting-started
    systems
    parameters
    encodings
    containers
    calibrators
    alarms
    commands
    verifiers
    algorithms
    expressions
    headers
    large-models
    generating

.. only:: html

   .. toctree::
       :maxdepth: 1
       :titlesonly:
       :caption: Appendices

       appendices/names
