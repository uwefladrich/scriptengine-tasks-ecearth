"""ScriptEngine-Tasks-ECEarth exceptions
"""


class MonitoringException(Exception):
    """Exceptions from the Monitoring Framework."""


class PresentationException(MonitoringException):
    """Raise this exception when errors occur during a presentation task."""


class InvalidMapTypeException(PresentationException):
    """Raise this exception when map type does not exist."""
