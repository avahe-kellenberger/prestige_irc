from irc_connection import IRCConnection
from commands import Commands
from connection import MessageListener


class ConnectionTest:

    def __init__(self, ip_address, enable_ssl=False):
        print("---Starting tests on connection.py---")
        self.irc_conn = IRCConnection("PrestigeBot")

        def receive(msg):
            print(msg)
            print("\r\n")
            if msg.command == Commands.PRIVMSG:
                if msg.args[0] == self.irc_conn.nick:
                    if msg.args[1].startswith("join"):
                        self.irc_conn.cmd_join(msg.args[1].split(" ")[1:])

        self.irc_conn.add_listener(MessageListener(lambda msg: True, receive=receive))

        if enable_ssl:
            self.irc_conn.connect_ssl(ip_address=ip_address, port=6697)
        else:
            self.irc_conn.connect(ip_address=ip_address, port=6667)
