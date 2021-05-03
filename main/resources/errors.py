__all__ = (
    "DuplicateFinderError",
    "PermissionsError",
)

class DuplicateFinderError(Exception):
    """Base class for all exceptions raised by this library"""
    pass


class PermissionsError(DuplicateFinderError):
    """Exception raised when cannot access a file"""
    pass