from __future__ import annotations

from yamcs.pymdb import xtce
from yamcs.pymdb.commands import Command
from yamcs.pymdb.containers import Container
from yamcs.pymdb.parameters import Parameter


class System:
    """
    The top-level system is the root element for the set of metadata
    necessary to monitor and command a space device, such as a satellite.

    A system defines a namespace.

    Metadata areas include: telemetry, calibration, alarm, algorithms and
    commands.

    A system may have child :class:`.Subsystem`\\s, forming a system tree.
    """

    def __init__(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
    ):
        self.name: str = name
        """Short name of this system"""

        self.aliases: dict[str, str] = aliases or {}
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = extra or {}
        """Arbitrary information, keyed by name"""

        self._commands_by_name: dict[str, Command] = {}
        self._containers_by_name: dict[str, Container] = {}
        self._parameters_by_name: dict[str, Parameter] = {}
        self._subsystems_by_name: dict[str, Subsystem] = {}

    @property
    def root(self) -> System:
        """
        The top-most system
        """
        return self

    @property
    def qualified_name(self) -> str:
        return "/" + self.name

    @property
    def containers(self) -> list[Container]:
        """
        Containers directly belonging to this system
        """
        copy = list(self._containers_by_name.values())
        copy.sort()
        return copy

    @property
    def commands(self) -> list[Command]:
        """
        Commands directly belonging to this system
        """
        copy = list(self._commands_by_name.values())
        copy.sort()
        return copy

    @property
    def parameters(self) -> list[Parameter]:
        """
        Parameters directly belonging to this system
        """
        copy = list(self._parameters_by_name.values())
        copy.sort()
        return copy

    @property
    def subsystems(self) -> list[Subsystem]:
        """
        Subsystems directly belonging to this system
        """
        copy = list(self._subsystems_by_name.values())
        copy.sort()
        return copy

    def remove_parameter(self, name: str) -> bool:
        """
        Removes a parameter directly belonging to this system.

        Raises an exception if no such parameter exists
        """
        try:
            self._parameters_by_name.pop(name)
            return True
        except KeyError:
            return False

    def remove_command(self, name: str) -> bool:
        """
        Removes a command directly belonging to this system.

        Raises an exception if no such command exists
        """
        try:
            self._commands_by_name.pop(name)
            return True
        except KeyError:
            return False

    def remove_container(self, name: str) -> bool:
        """
        Removes a container directly belonging to this system.

        Raises an exception if no such container exists
        """
        try:
            self._containers_by_name.pop(name)
            return True
        except KeyError:
            return False

    def remove_subsystem(self, name: str) -> bool:
        """
        Removes a subsystem directly belonging to this system.

        Raises an exception if no such subsystem exists
        """
        try:
            self._subsystems_by_name.pop(name)
            return True
        except KeyError:
            return False

    def find_parameter(self, name: str) -> Parameter:
        """
        Find a parameter belonging directly to this system.

        Raises an exception if no parameter is found
        """
        return self._parameters_by_name[name]

    def find_command(self, name: str) -> Command:
        """
        Find a command belonging directly to this system.

        Raises an exception if no command is found
        """
        return self._commands_by_name[name]

    def find_container(self, name: str) -> Container:
        """
        Find a container belonging directly to this system.

        Raises an exception if no container is found
        """
        return self._containers_by_name[name]

    def find_subsystem(self, name: str) -> Subsystem:
        """
        Find a subsystem belonging directly to this system.

        Raises an exception if no subsystem is found
        """
        return self._subsystems_by_name[name]

    def dump(self, fp, indent: str = "  ", top_comment: bool | str = True) -> None:
        """
        Serialize this system in XTCE format to a file-like object
        """
        xml = self.dumps(indent=indent, top_comment=top_comment)
        fp.write(xml)

    def dumps(self, indent: str = "  ", top_comment: bool | str = True) -> str:
        """
        Serialize this system to an XTCE formatted string
        """
        return xtce.XTCE12Generator(self).to_xtce(
            indent=indent,
            top_comment=top_comment,
        )

    def __lt__(self, other: System) -> bool:
        return self.qualified_name < other.qualified_name

    def __str__(self) -> str:
        return self.qualified_name


class Subsystem(System):
    """
    A subsystem is identical to a :class:`System`, but in addition keeps a reference
    to its parent system.
    """

    def __init__(
        self,
        system: System,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
    ):
        super().__init__(
            name=name,
            aliases=aliases,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
        )

        self.system: System = system
        """Parent system"""

        if name in system._subsystems_by_name:
            raise Exception(
                "System {} already contains a subsystem {}".format(
                    system.qualified_name, name
                )
            )

        system._subsystems_by_name[name] = self

    @property
    def root(self) -> System:
        """
        The top-most system
        """
        parent = self.system
        while parent:
            if isinstance(parent, Subsystem):
                parent = parent.system
            else:
                return parent

        return parent

    @property
    def qualified_name(self) -> str:
        """
        Fully qualified name of this system (absolute path)
        """
        path = "/" + self.name

        parent = self.system
        while parent:
            path = "/" + parent.name + path

            if isinstance(parent, Subsystem):
                parent = parent.system
            else:
                parent = None

        return path


class YamcsSystem:

    _instance = System(name="yamcs")

    @staticmethod
    def get_parameter(qualified_name: str):
        """
        Create a new parameter object for the given name.

        This can be used when referencing an item under the built-in
        /yamcs system.

        :param qualified_name: Fully qualified name under the /yamcs system.
        """
        if not qualified_name.startswith("/" + YamcsSystem._instance.name + "/"):
            raise Exception(
                "Qualified name should start with '/{}/'. Got: '{}'".format(
                    YamcsSystem._instance.name, qualified_name
                )
            )
        parts = qualified_name.split("/")

        system = YamcsSystem._instance
        for part in parts[2:-1]:
            try:
                system = system.find_subsystem(part)
            except KeyError:
                system = Subsystem(system, name=part)

        try:
            return system.find_parameter(parts[-1])
        except KeyError:
            return Parameter(system, name=parts[-1])
