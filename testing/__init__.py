from prestige_irc.commands import Commands
from prestige_irc.connection import MessageListener
from prestige_irc.irc_connection import IRCConnection

if __name__ == '__main__':

    def receive(msg):
        print(msg)
        print("\r\n")
        if msg.command == Commands.PRIVMSG:
            if msg.text.startswith("join "):
                irc_connection.cmd_join(msg.text.split(" ")[1:])
            elif msg.text.startswith("!repeat "):
                reply_location = msg.target if msg.target.startswith("#") else msg.nick
                irc_connection.cmd_privmsg(reply_location, " ".join(msg.text.split(" ")[1:]))
            elif msg.text.startswith("!pm "):
                irc_connection.cmd_privmsg(msg.nick, " ".join(msg.text.split(" ")[1:]))


    print("---Starting tests on connection.py---")
    irc_connection = IRCConnection("PrestigeBot")

    irc_connection.connect(ip_address="prestige_irc.rizon.net")
    listener = MessageListener(message_filter=lambda msg: True, receive=receive)
    irc_connection.add_listener(listener)
