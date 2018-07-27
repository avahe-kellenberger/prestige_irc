from testing.connection_test import ConnectionTest


if __name__ == '__main__':
    print("Initializing tests.")
    conn_test = ConnectionTest(ip_address="irc.rizon.net", enable_ssl=True)
