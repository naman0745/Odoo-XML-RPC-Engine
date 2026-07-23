import datetime
from dataclasses import dataclass
from typing import Optional

from connection.odoo_client import OdooClient


@dataclass
class AuthenticatedContext:
    """
    Represents the currently authenticated user session.
    Contains runtime state only and is not persisted to disk.
    """
    username: str
    uid: int
    client: OdooClient
    authenticated_at: datetime.datetime
    
    @property
    def is_connected(self) -> bool:
        return self.client is not None and self.uid is not None


class AuthenticationManager:
    """
    Primary entry point for Odoo authentication.
    Handles credential validation, context creation, and logout operations.
    """
    
    def __init__(self, url: str, db: str):
        self.url = url
        self.db = db
        self._context: Optional[AuthenticatedContext] = None

    @property
    def current_context(self) -> Optional[AuthenticatedContext]:
        """Exposes the current authentication state."""
        return self._context

    @property
    def is_authenticated(self) -> bool:
        return self._context is not None and self._context.is_connected

    def authenticate(self, username: str, password: str) -> AuthenticatedContext:
        """
        Validates credentials, initializes the Odoo connection, 
        and establishes an AuthenticatedContext upon success.
        """
        client = OdooClient(
            url=self.url,
            db=self.db,
            username=username,
            password=password
        )
        
        # OdooClient.connect() returns True or raises Exception, 
        # but we also need it to populate client.uid.
        try:
            if client.connect():
                self._context = AuthenticatedContext(
                    username=username,
                    uid=client.uid,
                    client=client,
                    authenticated_at=datetime.datetime.now()
                )
                return self._context
            else:
                self._context = None
                raise ConnectionError("Authentication failed: Connection refused.")
        except Exception as e:
            self._context = None
            raise e

    def logout(self) -> None:
        """Destroys the current authenticated session."""
        self._context = None
