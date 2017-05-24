import connection


class IRCConnection(connection.Connection):

    """Creates a connection to an IRC network."""
    
    def __init__(self):
        super().__init__()
        self.nick = None

    def connect(self, ip_address, port, timeout = 10):
        if super().connect(ip_address, port, timeout):

            self.add_listener(lambda data: (self.irc_parser(data)))
        else:
            print("Failed to connect to " + self.server + " at port " + self.port + ".")
            exit()

    def send_identity(self, s):
        # TODO: Research irc messaging system, change name of function and variable name.
        self.send("USER " + self.nick + " " + self.nick + " " + self.nick + " :" + s + "\n")

    def join(self, channels):
            """Joins the specified channels.

            Parameters
            ----------
            channels: collections.iterable
                A list of channels to join, prefixed with '#'.
            """
            for channel in channels:
                self.send("JOIN " + channel + "\n")
                
    def set_nick(self, nick):
        """Attempts to set the user's nick on the irc server.

        Parameters
        ----------
        nick: str
            The user's nick name.
        """
        # TODO: Review implementation
        self.send("NICK " + nick + "\n")
