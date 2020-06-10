"""ScriptEngine-Tasks-ECEarth exceptions
"""

class MonitoringException(Exception):
    """Exceptions from the Monitoring Framework."""

class InvalidMapTypeException(MonitoringException):
    """Raise this exception when map type does not exist."""