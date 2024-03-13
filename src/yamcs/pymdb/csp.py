from textwrap import dedent
from typing import NamedTuple

from yamcs.pymdb.commands import (
    ArgumentEntry,
    BooleanArgument,
    Command,
    EnumeratedArgument,
    FixedValueEntry,
    IntegerArgument,
)
from yamcs.pymdb.containers import Container, ParameterEntry
from yamcs.pymdb.datatypes import Choices
from yamcs.pymdb.encodings import uint1_t, uint2_t, uint5_t, uint6_t
from yamcs.pymdb.parameters import (
    BooleanParameter,
    EnumeratedParameter,
    IntegerParameter,
)
from yamcs.pymdb.systems import System


class CspHeader(NamedTuple):
    tm_container: Container
    tm_pri: EnumeratedParameter
    tm_src: EnumeratedParameter
    tm_dst: EnumeratedParameter
    tm_dport: IntegerParameter
    tm_sport: IntegerParameter
    tm_hmac: BooleanParameter
    tm_xtea: BooleanParameter
    tm_rdp: BooleanParameter
    tm_crc: BooleanParameter
    tc_container: Command
    tc_pri: EnumeratedArgument
    tc_src: EnumeratedArgument
    tc_dst: EnumeratedArgument
    tc_dport: IntegerArgument
    tc_hmac: BooleanArgument
    tc_xtea: BooleanArgument
    tc_rdp: BooleanArgument
    tc_crc: BooleanArgument


def add_csp_header(
    system: System,
    ids: Choices | None = None,
    prefix: str = "csp_",
) -> CspHeader:
    """
    Add a CSP header to the given system.

    :param system:
        System where to add parameters, commands and containers
    :param ids:
        If provided, model the ``csp_src`` and ``csp_dst`` parameters and
        arguments as enumerations, rather than integers.
    :param prefix:
        Prefix for all generated names.
    """
    tm_pri = EnumeratedParameter(
        system=system,
        name=f"{prefix}pri",
        short_description="Message priority",
        choices=[
            (0, "CRITICAL"),
            (1, "HIGH"),
            (2, "NORMAL"),
            (3, "LOW"),
        ],
        encoding=uint2_t,
    )

    tm_src = EnumeratedParameter(
        system=system,
        name=f"{prefix}src",
        short_description="Source",
        choices=ids if ids is not None else [],
        encoding=uint5_t,
    )

    tm_dst = EnumeratedParameter(
        system=system,
        name=f"{prefix}dst",
        short_description="Destination",
        choices=ids if ids is not None else [],
        encoding=uint5_t,
    )

    tm_dport = IntegerParameter(
        system=system,
        name=f"{prefix}dport",
        short_description="Destination port",
        signed=False,
        encoding=uint6_t,
    )

    tm_sport = IntegerParameter(
        system=system,
        name=f"{prefix}sport",
        short_description="Source port",
        signed=False,
        encoding=uint6_t,
    )

    tm_hmac = BooleanParameter(
        system=system,
        name=f"{prefix}hmac",
        short_description="Use HMAC verification",
        encoding=uint1_t,
    )

    tm_xtea = BooleanParameter(
        system=system,
        name=f"{prefix}xtea",
        short_description="Use XTEA encryption",
        encoding=uint1_t,
    )

    tm_rdp = BooleanParameter(
        system=system,
        name=f"{prefix}rdp",
        short_description="Use RDP protocol",
        encoding=uint1_t,
    )

    tm_crc = BooleanParameter(
        system=system,
        name=f"{prefix}crc",
        short_description="Use CRC32 checksum",
        encoding=uint1_t,
    )

    tm_container = Container(
        system=system,
        name=f"{prefix}message",
        abstract=True,
        short_description="CubeSat Space Protocol (CSP) header 1.x",
        long_description=dedent(
            """
            CSP Header 1.x

            The port range is divided into three adjustable segments.
            Ports 0 to 7 are used for general services such as ping and
            buffer status, and are implemented by the CSP service handler.
            The ports from 8 to 47 are used for subsystem specific services.
            All remaining ports, from 48 to 63, are ephemeral ports used for
            outgoing connections. The bits from 28 to 31 are used for marking
            packets with HMAC, XTEA encryption, RDP header and CRC32 checksum.
            """
        ),
        bits=32,
        entries=[
            ParameterEntry(tm_pri),
            ParameterEntry(tm_src),
            ParameterEntry(tm_dst),
            ParameterEntry(tm_dport),
            ParameterEntry(tm_sport),
            ParameterEntry(tm_hmac, location_in_bits=4),
            ParameterEntry(tm_xtea),
            ParameterEntry(tm_rdp),
            ParameterEntry(tm_crc),
        ],
    )

    tc_pri = EnumeratedArgument(
        name=f"{prefix}pri",
        short_description="Message priority",
        choices=[
            (0, "CRITICAL"),
            (1, "HIGH"),
            (2, "NORMAL"),
            (3, "LOW"),
        ],
        default="NORMAL",
        encoding=uint2_t,
    )

    tc_src = EnumeratedArgument(
        name=f"{prefix}src",
        short_description="Source",
        choices=ids if ids is not None else [],
        encoding=uint5_t,
    )

    tc_dst = EnumeratedArgument(
        name=f"{prefix}dst",
        short_description="Destination",
        choices=ids if ids is not None else [],
        encoding=uint5_t,
    )

    tc_dport = IntegerArgument(
        name=f"{prefix}dport",
        short_description="Destination port",
        signed=False,
        encoding=uint6_t,
    )

    tc_hmac = BooleanArgument(
        name=f"{prefix}hmac",
        short_description="Use HMAC verification",
        default=False,
        encoding=uint1_t,
    )

    tc_xtea = BooleanArgument(
        name=f"{prefix}xtea",
        short_description="Use XTEA encryption",
        default=False,
        encoding=uint1_t,
    )

    tc_rdp = BooleanArgument(
        name=f"{prefix}rdp",
        short_description="Use RDP protocol",
        default=False,
        encoding=uint1_t,
    )

    tc_crc = BooleanArgument(
        name=f"{prefix}crc",
        short_description="Use CRC32 checksum",
        default=False,
        encoding=uint1_t,
    )

    tc_container = Command(
        system=system,
        name=f"{prefix}message",
        abstract=True,
        short_description="CubeSat Space Protocol (CSP) header 1.x",
        long_description=dedent(
            """
            CSP Header 1.x

            The port range is divided into three adjustable segments.
            Ports 0 to 7 are used for general services such as ping and
            buffer status, and are implemented by the CSP service handler.
            The ports from 8 to 47 are used for subsystem specific services.
            All remaining ports, from 48 to 63, are ephemeral ports used for
            outgoing connections. The bits from 28 to 31 are used for marking
            packets with HMAC, XTEA encryption, RDP header and CRC32 checksum.
            """
        ),
        arguments=[
            tc_pri,
            tc_src,
            tc_dst,
            tc_dport,
            tc_hmac,
            tc_xtea,
            tc_rdp,
            tc_crc,
        ],
        entries=[
            ArgumentEntry(tc_pri),
            ArgumentEntry(tc_src),
            ArgumentEntry(tc_dst),
            ArgumentEntry(tc_dport),
            FixedValueEntry(
                name=f"{prefix}sport",
                binary=b"\x20",  # 48
                bits=6,
                short_description="Ephemeral port for outgoing connection",
            ),
            FixedValueEntry(name=f"{prefix}reserved", binary=b"\x00", bits=4),
            ArgumentEntry(tc_hmac),
            ArgumentEntry(tc_xtea),
            ArgumentEntry(tc_rdp),
            ArgumentEntry(tc_crc),
        ],
    )

    return CspHeader(
        tm_container,
        tm_pri,
        tm_src,
        tm_dst,
        tm_dport,
        tm_sport,
        tm_hmac,
        tm_xtea,
        tm_rdp,
        tm_crc,
        tc_container,
        tc_pri,
        tc_src,
        tc_dst,
        tc_dport,
        tc_hmac,
        tc_xtea,
        tc_rdp,
        tc_crc,
    )
