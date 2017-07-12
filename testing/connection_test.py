from irc_connection import IRCConnection
from commands import Commands
from connection import MessageListener


class ConnectionTest:
    
    def __init__(self, ip, port):
        print("---Starting tests on connection.py---")
        self.irc_conn = IRCConnection("PrestigeBot")

        def receive(msg):
            print(msg)
            print("\r\n")
            if msg.command == Commands.PRIVMSG.value:
                if msg.args[0] == self.irc_conn.nick:
                    if msg.args[1].startswith("join"):
                        self.irc_conn.cmd_join(msg.args[1].split(" ")[1:])

        self.irc_conn.add_listener(MessageListener(lambda msg: True, receive=receive))

        # TODO: IRCConnection.connect blocks thread; maybe run on new thread?
        # Idea: Add an optional param to create the connection on a new thread, and return the thread or None.
        self.irc_conn.connect(ip, port, 1000)

