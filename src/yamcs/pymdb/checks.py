from yamcs.pymdb.commands import ArrayArgument
from yamcs.pymdb.datatypes import FloatDataType
from yamcs.pymdb.encodings import ByteOrder, FloatDataEncoding, IntegerDataEncoding
from yamcs.pymdb.parameters import ArrayParameter
from yamcs.pymdb.systems import System
from yamcs.pymdb.verifiers import TerminationAction


def iter_parameter_data_types(system: System):
    for parameter in system.parameters:
        if isinstance(parameter, ArrayParameter):
            yield parameter.data_type
        else:
            yield parameter

    for subsystem in system.subsystems:
        yield iter_parameter_data_types(subsystem)


def iter_argument_data_types(system: System):
    for command in system.commands:
        for argument in command.arguments:
            if isinstance(argument, ArrayArgument):
                yield command, argument, argument.data_type
            else:
                yield command, argument, argument

    for subsystem in system.subsystems:
        subgen = iter_argument_data_types(subsystem)
        for a, b, c in subgen:
            yield a, b, c


def check_complete_verifiers(system: System):
    """
    Checks that all commands have at least one complete verifier that
    can completes the command
    """
    for command in system.commands:
        if command.abstract:
            continue

        match = False
        for verifier in command.verifiers:
            if verifier.on_success == TerminationAction.SUCCESS:
                match = True
                break
            if verifier.on_fail == TerminationAction.SUCCESS:
                match = True
                break
            if verifier.on_timeout == TerminationAction.SUCCESS:
                match = True
                break

        if not match:
            print(
                f"Command {command} has no verifier that can complete "
                "the command successfully"
            )

    for subsystem in system.subsystems:
        check_complete_verifiers(subsystem)


def check_float_encoding(system: System):
    """
    Check that the size of float parameters/arguments is consistent with its data
    encoding.

    A common mistake is to have a float of 32 bits, with an encoding of 64 bits.
    """
    for data_type in iter_parameter_data_types(system):
        if isinstance(data_type, FloatDataType) and isinstance(
            data_type.encoding, FloatDataEncoding
        ):
            if data_type.bits == 32 and data_type.encoding.bits == 64:
                print(
                    f"Parameter {data_type}: float bits (32) is "
                    "smaller than encoding (64)"
                )

    for command, argument, data_type in iter_argument_data_types(system):
        if isinstance(data_type, FloatDataType) and isinstance(
            data_type.encoding, FloatDataEncoding
        ):
            if data_type.bits == 32 and data_type.encoding.bits == 64:
                print(
                    f"Command {command}: argument {argument.name} float bits (32) is "
                    "smaller than encoding (64)"
                )


def check_little_endian_only(system: System):
    """
    Check that data types use ony little endian encodings.
    """
    for parameter in system.parameters:
        data_type = parameter
        if isinstance(parameter, ArrayParameter):
            data_type = parameter.data_type

        encoding = data_type.encoding
        if isinstance(encoding, IntegerDataEncoding):
            if (
                encoding.byte_order != ByteOrder.LITTLE_ENDIAN
                and encoding.bits
                and encoding.bits > 8
            ):
                print(f"Parameter {parameter} is not in little endian")

    for command in system.commands:
        for argument in command.arguments:
            data_type = argument
            if isinstance(argument, ArrayArgument):
                data_type = argument.data_type

            encoding = data_type.encoding
            if isinstance(encoding, IntegerDataEncoding):
                if (
                    encoding.byte_order != ByteOrder.LITTLE_ENDIAN
                    and encoding.bits
                    and encoding.bits > 8
                ):
                    print(
                        f"Command {command}: argument {argument.name} "
                        "is not in little endian"
                    )

    for subsystem in system.subsystems:
        check_little_endian_only(subsystem)
