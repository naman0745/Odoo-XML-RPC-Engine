from connection.odoo_client import OdooClient


def main():

    client = OdooClient()

    if client.connect():
        print("Connected Successfully")
        print(client.uid)
    else:
        print("Failed to connect")


if __name__ == "__main__":
    main()