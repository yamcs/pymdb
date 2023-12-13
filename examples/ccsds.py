from yamcs.pymdb import ArgumentEntry, IntegerArgument, System, ccsds, uint16_t, xtce

spacecraft = System("Spacecraft")
ccsds_header = ccsds.add_ccsds_header(spacecraft)

command_id = IntegerArgument(
    name="command_id",
    signed=False,
    encoding=uint16_t,
)

project_command = spacecraft.add_command(
    name="MyProjectPacket",
    abstract=True,
    parent=ccsds_header.tc_command,
    assignments={
        ccsds_header.tc_secondary_header.name: "NotPresent",
        ccsds_header.tc_apid.name: 101,
    },
    arguments=[
        command_id,
    ],
    entries=[
        ArgumentEntry(command_id),
    ],
)

reboot_command = spacecraft.add_command(
    parent=project_command,
    name="Reboot",
    assignments={command_id.name: 1},
)

switch_voltage_on = spacecraft.add_command(
    parent=project_command,
    name="SwitchVoltageOn",
    short_description="Switches a battery on",
    assignments={command_id.name: 2},
    arguments=[
        IntegerArgument(
            name="battery",
            short_description="Number of the battery",
            signed=False,
            minimum=1,
            maximum=3,
            encoding=uint16_t,
        ),
    ],
)

switch_voltage_off = spacecraft.add_command(
    parent=project_command,
    name="SwitchVoltageOff",
    short_description="Switches a battery off",
    assignments={command_id.name: 3},
    arguments=[
        IntegerArgument(
            name="battery",
            short_description="Number of the battery",
            signed=False,
            minimum=1,
            maximum=3,
            encoding=uint16_t,
        ),
    ],
)


with open("ccsds.xml", "wt") as f:
    xtce.dump(spacecraft, f)
