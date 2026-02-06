class ExportError(Exception):
    """An error occurred while generating an export."""


class SizeCalculationError(ValueError):
    """Bit size cannot be determined."""


class DuplicateNameError(ValueError):
    """An object is added to a system with a name that is already in use."""
