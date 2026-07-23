"""
connection/exceptions.py
Custom exceptions for Odoo networking and authentication states.
"""

class OdooConnectionError(Exception):
    """Base class for all Odoo connection-related exceptions."""
    pass

class ConnectionLostError(OdooConnectionError):
    """Raised when the application cannot reach the Odoo server due to network dropouts."""
    pass

class AuthenticationExpiredError(OdooConnectionError):
    """Raised when the Odoo server rejects a command due to expired or missing token/password."""
    pass
