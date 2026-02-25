from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, TextIO
from enum import Enum

from functools import total_ordering
import re

class ValidationStatus(str, Enum):
    UNKNOWN = "Unknown"
    WORKING = "Working"
    DRAFT = "Draft"
    TEST = "Test"
    VALIDATED = "Validated"
    RELEASED = "Released"
    WITHDRAWN = "Withdrawn"

@total_ordering
class History:
    __slots__ = ("version", "date", "message", "author")

    def __init__(
        self,
        version: str,
        date: str | None = None,
        message: str | None = None,
        author: str | None = None,
    ):
        if version is None:
            raise ValueError("Version can not be null")

        if not re.match(r"[0-9]+.*", version):
            raise ValueError(f"Invalid version format '{version}'")

        self.version: str = version
        self.date: str | None = date
        self.message: str | None = message
        self.author: str | None = author

    def __str__(self) -> str:
        base = f"{self.version}"
        base = f"{base}; {self.date}" if self.date else f"{base}; "
        base = f"{base}; {self.message}" if self.message else f"{base}; "
        base = f"{base}; {self.author}" if self.author else f"{base}; "

        return base

    def _version_parts(self) -> list[str]:
        return self.version.split(".")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, History):
            return NotImplemented
        return self._compare_versions(other) == 0

    def __lt__(self, other: History) -> bool:
        if other is None:
            return False
        return self._compare_versions(other) < 0

    def _compare_versions(self, other: History) -> int:
        parts = self._version_parts()
        oparts = other._version_parts()

        length = max(len(parts), len(oparts))

        for i in range(length):
            p = parts[i] if i < len(parts) else "0"
            o = oparts[i] if i < len(oparts) else "0"

            try:
                pi = int(p)
                oi = int(o)
                if pi != oi:
                    return -1 if pi < oi else 1
            except ValueError:
                if p != o:
                    return -1 if p < o else 1

        return 0

class Header:
    __slots__ = ("_version", "_date", "_history_list", "_author_list", "_validation_status", "_classification", "_classification_instructions")

    def __init__(self, validation_status: str | ValidationStatus) -> None:
        self._version: str | None = None
        self._date: str | None = None
        self._history_list: list[History] = []
        self._author_list: list[str] = []
        self._classification: str = "NotClassified"
        self._classification_instructions: str | None = None

        # Mandatory field
        self.validation_status: ValidationStatus = validation_status

    # setters
    def set_version(self, version: str | None) -> None:
        self._version = version

    def set_date(self, date: str | None) -> None:
        self._date = date

    def set_classification(self, classification: str | None) -> None:
        if classification:
            self._classification = classification

    def set_classification_instructions(self, instructions: str | None) -> None:
        self._classification_instructions = instructions

    @property
    def validation_status(self) -> str:
        return self._validation_status.value

    @validation_status.setter
    def validation_status(self, value: str | ValidationStatus) -> None:

        if isinstance(value, ValidationStatus):
            self._validation_status = value
            return

        if isinstance(value, str):
            try:
                self._validation_status = ValidationStatus(value)
                return
            except ValueError:
                pass

        raise ValueError(
            f"Invalid validation status: {value!r}. "
            f"Allowed: {[s.value for s in ValidationStatus]}"
        )

    # getters
    def get_classification(self) -> str:
        return self._classification

    def get_classification_instructions(self) -> str | None:
        return self._classification_instructions
    
    def get_version(self) -> str | None:
        return self._version

    def get_date(self) -> str | None:
        return self._date

    def get_history_list(self) -> list[History]:
        return self._history_list

    def get_author_list(self) -> list[str]:
        return self._author_list

    def add_history(self, history: History) -> None:
        self._history_list.append(history)

    def add_author(self, author: str) -> None:
        self._author_list.append(author)


    def __str__(self) -> str:
        return f"version: {self._version}, date: {self._date}"
