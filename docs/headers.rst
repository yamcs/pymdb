======================
CCSDS and CSP Headers
======================

.. index:: CCSDS
.. index:: CSP

Many missions prefix their telemetry and telecommands with a standard
header. Two common ones are CCSDS Space Packets and the CubeSat Space
Protocol (CSP); other standard and mission-specific headers exist but are
not covered here. PyMDB ships ready-made helpers for CCSDS and CSP, in the
``yamcs.pymdb.ccsds`` and ``yamcs.pymdb.csp`` modules. Each helper adds the
header parameters, an abstract telemetry container and an abstract command
to a system, and returns handles to everything it created — so your own
packets and commands can extend them.

These helpers are also worth reading as *source code*: they are compact,
idiomatic examples of container/command inheritance, and a template for
writing an equivalent helper for a mission-specific header.


CCSDS Space Packets
===================

.. index:: CcsdsHeader

``ccsds.add_ccsds_header(system)`` models the 6-byte primary header of
CCSDS 133.0-B-1. It returns a ``CcsdsHeader`` named tuple with:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Field
     - Contents
   * - ``tm_container``
     - Abstract container ``ccsds_space_packet`` with the primary header
   * - ``tm_version``, ``tm_type``, ``tm_secondary_header``, ``tm_apid``
     - ``ParameterMember`` references into the header, ready for use in
       conditions
   * - ``tc_command``
     - Abstract command ``ccsds_space_packet`` encoding the header
   * - ``tc_secondary_header``, ``tc_apid``
     - The command's free arguments

Telemetry packets extend ``tm_container`` and identify themselves by APID
(and other fields as needed):

.. code-block:: python

   import yamcs.pymdb as Y
   from yamcs.pymdb import ccsds

   spacecraft = Y.System("Spacecraft")
   header = ccsds.add_ccsds_header(spacecraft)

   eps_hk = Y.Container(
       system=spacecraft,
       name="eps_hk",
       base=header.tm_container,
       condition=Y.eq(header.tm_apid, 101),
       entries=[
           # payload fields, positioned after the primary header
       ],
   )

Commands extend ``tc_command``, typically through an intermediate abstract
command that pins the APID once and adds a mission-specific field such as
a command ID:

.. code-block:: python

   command_id = Y.IntegerArgument(name="command_id", signed=False,
                                  encoding=Y.uint16_t)

   project_command = Y.Command(
       system=spacecraft,
       name="MyProjectPacket",
       abstract=True,
       base=header.tc_command,
       assignments={
           header.tc_secondary_header.name: "NotPresent",
           header.tc_apid.name: 101,
       },
       arguments=[command_id],
   )

   reboot = Y.Command(
       system=spacecraft,
       name="Reboot",
       base=project_command,
       assignments={command_id.name: 1},
   )

In the generated command, the sequence count and packet length fields are
zeroed fixed-value entries: Yamcs fills them in during link
post-processing.


CubeSat Space Protocol
======================

.. index:: CspHeader

``csp.add_csp_header(system, ids=None, prefix="csp_")`` models the 32-bit
CSP 1.x header, with its priority, source/destination addresses and ports,
and the HMAC/XTEA/RDP/CRC flags.

``ids``
    Optional list of ``(address, name)`` pairs, in the same format as
    enumeration choices (see :doc:`../parameters`). When given, the source
    and destination fields become enumerations instead of plain integers,
    so Yamcs displays node names.

``prefix``
    Prefix for all generated names (default ``csp_``), allowing several
    header sets in one system.

The returned ``CspHeader`` named tuple exposes the telemetry container
(``tm_container``), the abstract command (``tc_container``), and each
individual parameter and argument (``tm_pri``, ``tm_src``, ``tm_dst``,
``tm_dport``, ``tm_sport``, flag parameters, and the ``tc_*``
equivalents).

.. code-block:: python

   import yamcs.pymdb as Y

   satellite = Y.System("MySat")
   csp = Y.csp.add_csp_header(satellite, ids=[
       (1, "UHF Radio"),
       (3, "FC"),
       (4, "EPS"),
   ])

   eps_telemetry = Y.Container(
       system=satellite,
       name="eps_telemetry",
       base=csp.tm_container,
       condition=Y.all_of(
           Y.eq(csp.tm_src, "EPS"),
           Y.eq(csp.tm_dport, 7),
       ),
   )

As with CCSDS, commands derive from ``csp.tc_container``, assigning the
destination address and port per subsystem or service.

The returned handles are ordinary PyMDB objects and can be adjusted after
the call — for example setting ``csp.tc_src.default`` to the ground
station's own address, or filling in ``choices`` on the address fields
later, once the node list is assembled.
