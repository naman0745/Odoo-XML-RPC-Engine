import xmlrpc.client
import socket
from functools import wraps

from connection.exceptions import AuthenticationExpiredError, ConnectionLostError

def translate_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except xmlrpc.client.Fault as e:
            if "Access Denied" in str(e.faultString) or getattr(e, 'faultCode', getattr(e, 'faultcode', None)) in (1, '1'):
                raise AuthenticationExpiredError("Your session has expired. Please log in again.")
            raise
        except xmlrpc.client.ProtocolError as e:
            if e.errcode in (401, 403):
                raise AuthenticationExpiredError("Your session has expired. Please log in again.")
            raise ConnectionLostError(f"Protocol error communicating with Odoo: {e.errmsg}")
        except (ConnectionRefusedError, socket.error, TimeoutError, OSError):
            raise ConnectionLostError("Connection to the Odoo server was lost. Please check your network or server status.")
    return wrapper


class OdooClient:

    def __init__(self, url, db, username, password):

        self.url = url
        self.db = db
        self.username = username
        self.password = password

        self.uid = None
        self.models = None

    @translate_exceptions
    def connect(self):

        common = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/common"
        )

        self.uid = common.authenticate(
            self.db,
            self.username,
            self.password,
            {}
        )

        if not self.uid:
            raise Exception("Authentication failed.")

        self.models = xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/object"
        )

        print("Connected Successfully")
        print(f"User ID : {self.uid}")

        return True
    
    @translate_exceptions
    def search(self, model, domain):
        
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "search",
            [domain]
        )
        
    @translate_exceptions
    def read(self, model, ids, fields=None):
        kwargs = {}

        if fields:
            kwargs["fields"] = fields

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "read",
            [ids],
            kwargs
        )
            
    @translate_exceptions
    def search_read(self, model, domain, fields=None, limit=None):
        kwargs = {}

        if fields:
            kwargs["fields"] = fields

        if limit:
            kwargs["limit"] = limit

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "search_read",
            [domain],
            kwargs
        )
            
    @translate_exceptions
    def name_search(self, model, name, operator="ilike", limit=100):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "name_search",
            [name],
            {
                "operator": operator,
                "limit": limit
            }
        )

    @translate_exceptions
    def create(self, model, values):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "create",
            [values]
        )

    @translate_exceptions
    def write(self, model, ids, values):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "write",
            [ids, values]
        )

    @translate_exceptions
    def unlink(self, model, ids):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "unlink",
            [ids]
        )
