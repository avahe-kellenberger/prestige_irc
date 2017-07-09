from irc_connection import IRCConnection


class ConnectionTest:
    
    def __init__(self, ip, port):
        print("---Starting tests on connection.py---")
        self.irc_conn = IRCConnection("PrestigeBot")
        # TODO: IRCConnection.connect blocks thread; maybe run on new thread?
        # Idea: Add an optional param to create the connection on a new thread, and return the thread or None.
        self.irc_conn.connect(ip, port, 1000)
