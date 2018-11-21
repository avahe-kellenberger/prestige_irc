from commands import Commands
from connection import MessageListener
from irc_connection import IRCConnection


class ConnectionTest:

    def __init__(self, ip_address, enable_ssl=False):
        print("---Starting tests on connection.py---")
        self.irc_conn = IRCConnection("PrestigeBot")

        def receive(msg):
            print(msg)
            print("\r\n")
            if msg.command == Commands.PRIVMSG:
                if msg.text.startswith("join "):
                    self.irc_conn.cmd_join(msg.text.split(" ")[1:])
                elif msg.text.startswith("!repeat "):
                    reply_location = msg.target if msg.target.startswith("#") else msg.nick
                    self.irc_conn.cmd_privmsg(reply_location, " ".join(msg.text.split(" ")[1:]))
                elif msg.text.startswith("!pm "):
                    self.irc_conn.cmd_privmsg(msg.nick, " ".join(msg.text.split(" ")[1:]))

        self.irc_conn.add_listener(MessageListener(lambda msg: True, receive=receive))

        port = 6697 if enable_ssl else 6667
        self.irc_conn.connect(ip_address=ip_address, port=port, enable_ssl=enable_ssl)
