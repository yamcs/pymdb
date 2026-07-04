=============================
Containers: Telemetry Packets
=============================

.. index:: Container

A ``Container`` describes the binary layout of a telemetry packet: which
parameters appear, in what order, and at which bit positions. When Yamcs
receives a packet, it matches it against the containers of the MDB and
extracts the parameter values.

.. code-block:: python

   hk = Y.Container(
       system=eps,
       name="hk_packet",
       short_description="EPS housekeeping",
       entries=[
           Y.ParameterEntry(mode),
           Y.ParameterEntry(voltage),
           Y.ParameterEntry(current),
       ],
   )

Every parameter referenced from a container must have an
:doc:`encoding <encodings>`; the encoding determines how many bits each
entry occupies.


Entry positioning
=================

.. index:: ParameterEntry

By default entries are packed consecutively: each entry starts where the
previous one ended. Two options adjust this, on ``ParameterEntry`` as well
as ``ContainerEntry``:

``bitpos``
    Absolute position from the start of the container, in bits.

``offset``
    Gap in bits relative to the end of the preceding entry. Useful to skip
    padding or reserved fields without defining a parameter for them.

.. code-block:: python

   entries=[
       Y.ParameterEntry(flags),
       Y.ParameterEntry(voltage, offset=4),   # skip 4 reserved bits
       Y.ParameterEntry(footer, bitpos=112),  # pinned position
   ]

An entry can also be conditional: with ``condition`` set to an
:doc:`expression <expressions>`, the entry is only extracted when the
condition — usually on a parameter appearing earlier in the packet —
holds:

.. code-block:: python

   Y.ParameterEntry(payload_temp, condition=Y.eq(payload_on, True))


Container inheritance and packet identification
===============================================

.. index:: container inheritance
.. index:: restriction criteria

Real telemetry streams carry many packet types that share a common header.
This is modelled with container *inheritance*: a base container describes
the header, and each concrete packet extends it with a ``condition`` (the
XTCE "restriction criteria") stating when it applies.

.. code-block:: python

   # The base: common header, never instantiated on its own
   header = Y.Container(
       system=spacecraft,
       name="header",
       abstract=True,
       entries=[
           Y.ParameterEntry(packet_type),
           Y.ParameterEntry(packet_length),
       ],
   )

   # A concrete packet: applies when packet_type == 3
   eps_hk = Y.Container(
       system=spacecraft,
       name="eps_hk",
       base=header,
       condition=Y.eq(packet_type, 3),
       entries=[
           Y.ParameterEntry(voltage),
           Y.ParameterEntry(current),
       ],
   )

The derived container's entries start right after the base container's
entries. When Yamcs receives a packet, it starts at the root container and
descends to the most specific container whose conditions match — here,
``eps_hk`` for packets with ``packet_type == 3``.

``abstract=True`` marks a container that only serves as a base and never
identifies a packet by itself. ``base`` may also be a string with a
qualified name, for referencing a container that is not part of the PyMDB
model. For ready-made CCSDS and CSP header containers, see :doc:`headers`.

Inheritance chains can go as deep as the protocol requires. Layered formats
are modelled naturally by letting each level contribute its discriminator:
a first level selecting the source device, a second the packet type within
that device, a third the record type within the packet — each a container
extending the previous one with its own ``condition``. Yamcs descends the
chain level by level until it reaches the most specific match.

.. index:: ContainerEntry

A container can also *embed* another container as an entry, with
``ContainerEntry(other_container)`` — useful when a group of fields recurs
in the middle of several packets.

.. note::

   *Container* and *packet* are used loosely as synonyms in this manual,
   but they are not quite the same thing. A container is a structural
   definition — a named, ordered sequence of entries; a packet is the
   actual bytes Yamcs receives over a link. They coincide for the simple,
   common case: a non-abstract container with no base identifies a packet
   all by itself. But an ``abstract`` container never does — it only
   contributes entries to whatever extends it — and a container reached
   through ``ContainerEntry`` only covers a sub-span *within* a bigger
   packet, not a packet of its own. So one packet is generally identified
   through *several* containers at once: the whole inheritance chain from
   the root down to the most specific match, plus any containers embedded
   along the way.


Sizing
======

Yamcs derives the size of a container from its entries, so most containers
need no explicit size. Stating one can still be useful:

``bits``
    Fixed container size in bits. When this container is included in, or
    extended by, others, a known fixed size lets Yamcs jump over it
    without inspecting the entries, speeding up extraction. When the
    container extends a base, ``bits`` includes the base's size.

``fit_entries()``
    Computes ``bits`` from the (fixed-size) entries, so you don't have to
    keep a manual count in sync. Raises ``SizeCalculationError`` when a
    size cannot be determined (e.g. dynamic arrays).


Expiration and storage
======================

``rate``
    Expected update interval in seconds — ``rate=2`` means one update
    every 2 seconds. Yamcs uses it to mark parameter values as *expired*
    when no fresh packet arrives in time (after ``1.9 × rate``, with a
    configurable tolerance factor). Without a rate, values never expire.

``hint_partition``
    When ``True``, hints Yamcs to partition its archive by this
    container's name. Consider it for high-volume packet types that are
    typically queried separately.
