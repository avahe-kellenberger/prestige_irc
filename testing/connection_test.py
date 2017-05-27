from irc_connection import IRCConnection
from irc import IRC


class ConnectionTest:
    
    def __init__(self, ip, port):
        print("---Starting tests on connection.py---")
        self.irc_conn = IRCConnection("PrestigeBot")
        self.irc_conn.connect(ip, port, 10000000)
