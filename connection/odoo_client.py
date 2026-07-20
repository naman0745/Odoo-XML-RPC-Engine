import xmlrpc.client

from config.settings import (
    ODOO_URL,
    ODOO_DB,
    ODOO_USERNAME,
    ODOO_PASSWORD
)


class OdooClient:

    def __init__(self):

        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD

        self.uid = None
        self.models = None

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
    
    def search(self, model, domain):
        
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "search",
            [domain]
        )
        
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

    def create(self, model, values):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "create",
            [values]
        )

    def write(self, model, ids, values):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "write",
            [ids, values]
        )

    def unlink(self, model, ids):
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            "unlink",
            [ids]
        )
