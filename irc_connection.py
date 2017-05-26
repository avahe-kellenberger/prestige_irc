import connection
from irc import IRC


class IRCConnection(connection.Connection):

    """Creates a connection to an IRC network."""
    
    def __init__(self):
        super().__init__()
        self.nick = None

    def connect(self, ip_address, port, timeout=10):
        """Attempts to connect to the specified IP address and port.

        Parameters
        ----------
        ip_address: str
            The IP address to connect to.
        port: int
            The port number to bind to.
        timeout: int (optional)
            The number of seconds to wait to stop attempting to connect if a connection has not yet been made.
            Default value is 10.

        Returns
        -------
        bool:
            If the connection was successfully established.
        """

        success = super().connect(ip_address, port, timeout)
        if success:
            self.add_listener(lambda data: (IRC.parse(data)))
        else:
            print("Failed to connect to " + ip_address + " at port " + str(port) + ".")
        return success

    def send_message(self, channel_or_user, message):
        """Send a message to a channel or a user.

        Parameters
        ----------
        channel_or_user: str
            The user or channel to send a message to. If a channel, it must be prefixed with '#'.
        message: str
            The message to send.
        """

        self.send("PRIVMSG " + channel_or_user + " :" + message)

    def send_user(self, real_name, invisible=False):
        """Sends the user data to the server. This is done automatically upon calling IRCConnection.connect, using
        IRCConnection.nick as the default for real_name.

        Parameters
        ----------
        real_name: str
            The user's 'real name' which is visible to other members on the irc network.
        invisible: bool (optional)
            If the user wishes to remain invisible to other members on the network, aside from other members in the same
            channel(s).
            Default value is False.
        """

        self.send("USER " + self.nick + " " + str(8 if invisible else 0) + " * :" + real_name)

    def join(self, channels):
            """Joins the specified channels.

            Parameters
            ----------
            channels: collections.iterable
                A list of channels, prefixed with '#'
                This method automatically adds a '#' to the channel name if it is absent.
            """

            self.send("JOIN :" + ",".join("#" + channel if channel[0] != '#' else channel for channel in channels))

    def part(self, channels, reason=""):
            """Leaves the specified channels.

            Parameters
            ----------
            channels: collections.iterable
                A list of channels, prefixed with '#'
                This method automatically adds a '#' to the channel name if it is absent.
            reason: str (optional)
                The reason for leaving the channel(s).
                Default value is an empty string.
            """

            self.send("PART " +
                      ",".join("#" + channel if channel[0] != '#' else channel for channel in channels) + " :" + reason)

    def set_nick(self, nick):
        """Attempts to set the user's nick on the irc server.

        Parameters
        ----------
        nick: str
            The user's nick name.
        """
        # TODO: Review implementation
        self.send("NICK :" + nick)

    def pong(self, message):
        """Sends a pong message to the server.

        Parameters
        ----------
        message: str
            The message to send to the server.
        """
        # TODO: check if 'message' needs to be the same message in the server's PING message.
        self.send("PONG :" + message)

    def quit(self, reason=""):
        """Terminates the connection with the server, and sends an optional reason for quitting.

        Parameters
        ----------
        reason: str (optional)
            The reason for terminating the connection.
            Default is an empty string.
        """

        self.send("QUIT :" + reason)
