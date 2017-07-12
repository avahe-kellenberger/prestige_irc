import connection
from connection import MessageListener
from irc import IRCMessage
from commands import Commands


class IRCConnection(connection.Connection):

    """Creates a connection to an IRC network."""

    def __init__(self, nick):
        """
        Readies the connection to the irc, sets up the initial nick name to use.

        Parameters
        ----------
        nick: str
            The irc nick name to use.
        """
        super().__init__()
        # This queue is used for caching commands while the connection waits to be verified.
        # The commands will then be executed in the order the were called.
        self.__command_queue = []
        # If the server has welcomed the user (used for managing the command queue).
        self.__welcomed = False
        # The possible codes the server can send to welcome the user.
        self.__welcome_codes = ("001", "002", "003", "004")
        # Set the local user nickname.
        self.__nick = nick
        # Add the default listener, which handles basic IRC functionality.
        self.add_listener(self.__default_server_listener())

    def __default_server_listener(self):
        def receive(irc_message):
            """
            Automatically handles required user, nick, and ping responses.

            Parameters
            ----------
            irc_message: IRCMessage
                The message received by the server interpreted into an IRCMessage.
            """
            print(irc_message)
            print("\r\n")

            if irc_message.command == Commands.PRIVMSG.value:
                if irc_message.args[0] == self.__nick:
                    if irc_message.args[1].startswith("join"):
                        self.cmd_join(irc_message.args[1].split(" ")[1:])

            # Send proper response to PING messages.
            if irc_message.command == Commands.PING.value:
                self.cmd_pong(irc_message.args[0])
                return

            # Once the hostname has been found, user and nick message can be sent.
            if irc_message.command == Commands.NOTICE.value:
                for string in irc_message.args:
                    if "*** Found your hostname" in string:
                        self.cmd_nick(self.__nick, wait_for_welcome=False)
                        self.cmd_user(self.__nick, wait_for_welcome=False)
                        return

            # Welcome message received.
            if not self.__welcomed and irc_message.command in self.__welcome_codes:
                self.__welcomed = True
                # Fire commands in queue.
                for command in self.__command_queue:
                    self.send_command(command[0], command[1], command[2])
        return MessageListener(lambda msg: True, receive)

    def _process_data(self, data):
        """Processes the bytes that are received from the server, and converts them into an IRCMessage."""
        return IRCMessage(data.decode("utf-8"))

    def connect(self, ip_address, port, timeout=10):
        """
        Attempts to connect to the specified IP address and port.

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
        return super().connect(ip_address, port, timeout)

    def nick(self):
        """
        Gets the user's nick.

        Returns
        -------
        str:
            The user's nick.
        """
        return self.__nick

    # --------------------------- #
    # IRC Commands Implementation #
    # --------------------------- #

    def send_command(self, command, prefix="", params="", wait_for_welcome=True):
        """
        Sends commands to the server. All functions prefixed with 'cmd' pass through this method.

        The message sent will be:
            prefix + command + " " + params

        Parameters
        ----------
        command: str
            The irc command, which can be found in commands.Commands.
        prefix: str (optional)
            A prefix to the command.
            Default value is an empty string.
        params: str (optional)
            The parameters of the command, in one string.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.

        Returns
        -------
        bool:
            If the message was sent successfully.
            If False is returned, this typically means the connection has been terminated.
        """
        if self.is_connection_alive():
            if self.__welcomed or not wait_for_welcome:
                self.send(prefix + command + (" " + params) if params else "")
            else:
                self.__command_queue.append((command, prefix, params))
        else:
            self.__welcomed = False
            return False
        return True

    def cmd_admin(self, target="", wait_for_welcome=True):
        """
        Instructs the server to return information about the administrators of the server specified by <target>,
        where <target> is either a server or a user. If <target> is omitted, the server should return information
        about the administrators of the current server.

        Parameters
        ----------
        target: str (optional)
            A server or a user.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.ADMIN.value, params=target, wait_for_welcome=wait_for_welcome)

    def cmd_away(self, message="", wait_for_welcome=True):
        """
        Provides the server with a <message> to automatically send in reply to a PRIVMSG directed at the user,
        but not to a channel they are on. If <message> is omitted, the away status is removed.

        Parameters
        ----------
        message: str (optional)
            The away message to send to the server.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.AWAY.value, params=message, wait_for_welcome=wait_for_welcome)

    def cmd_cnotice(self, nickname, channel, message, wait_for_welcome=True):
        """
        Sends a channel NOTICE message to <nickname> on <channel> that bypasses flood protection limits.
        The target nickname must be in the same channel as the client issuing the command,
        and the client must be a channel operator.

        Normally an IRC server will limit the number of different targets a client can send messages to within
        a certain time frame to prevent spammers or bots from mass-messaging users on the network,
        however this command can be used by channel operators to bypass that limit in their channel.
        For example, it is often used by help operators that may be communicating with a large number of users
        in a help channel at one time.

        This command is not formally defined in an RFC, but is in use by some IRC networks.
        Support is indicated in a RPL_ISUPPORT reply (numeric 005) with the CNOTICE keyword.

        Parameters
        ----------
        nickname: str
            The nick of the user to send the notice to.
        channel: str
            The channel the user is on to send the notice through.
        message: str
            The notice message to send to the user.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.CNOTICE.value,
                          params=nickname + " " + channel + " :" + message,
                          wait_for_welcome=wait_for_welcome)

    def cmd_cprivmsg(self, nickname, channel, message, wait_for_welcome=True):
        """
        Sends a private message to <nickname> on <channel> that bypasses flood protection limits.
        The target nickname must be in the same channel as the client issuing the command,
        and the client must be a channel operator.

        Normally an IRC server will limit the number of different targets a client can send messages to within
        a certain time frame to prevent spammers or bots from mass-messaging users on the network,
        however this command can be used by channel operators to bypass that limit in their channel.
        For example, it is often used by help operators that may be communicating with a large number of users
        in a help channel at one time.

        This command is not formally defined in an RFC, but is in use by some IRC networks.
        Support is indicated in a RPL_ISUPPORT reply (numeric 005) with the CPRIVMSG keyword.

        Parameters
        ----------
        nickname: str
            The nick of the user to send the message to.
        channel: str
            The channel the user is on to send the message through.
        message: str
            The message to send the user.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.CPRIVMSG.value,
                          params=nickname + " " + channel + " :" + message, wait_for_welcome=wait_for_welcome)

    def cmd_connect(self, target_server, port, remote_server=None, wait_for_welcome=True):
        """
        Instructs the server <remote server> (or the current server, if <remote server> is omitted)
        to connect to <target server> on port <port>.
        This command should only be available to IRC Operators.

        Parameters
        ----------
        target_server: str
            The name of the server to connect the remove_server to.
        port: int
            The port number to connect to.
        remote_server: str (optional)
            The remote server to connect the target sever to.
            If omitted, this parameter will use the current server.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.CONNECT.value,
                          params=target_server + " " + str(port) + (" " + remote_server) if remote_server else "",
                          wait_for_welcome=wait_for_welcome)

    def cmd_die(self, wait_for_welcome=True):
        """
        This command may only be issued by IRC server operators.
        Instructs the server to shut down.

        Parameters
        ----------
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.DIE.value, wait_for_welcome=wait_for_welcome)

    def cmd_encap(self, destination, subcommand, parameters, wait_for_welcome=True):
        """
        This command is for use by servers to encapsulate commands so that they will propagate across
        hub servers not yet updated to support them, and indicates the subcommand and its parameters should be passed
        unaltered to the destination, where it will be unencapsulated and parsed.
        This facilitates implementation of new features without a need to restart all servers before they are
        usable across the network.

        Parameters
        ----------
        destination: str
            The hub server destination.
        subcommand: str
            The command to send/
        parameters: str
            The parameters of the command being sent.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.ENCAP.value,
                          params=destination + " " + subcommand + " " + parameters, wait_for_welcome=wait_for_welcome)

    def cmd_error(self, error_message, wait_for_welcome=True):
        """
        This command is for use by servers to report errors to other servers.
        It is also used before terminating client connections.

        Parameters
        ----------
        error_message: str
            The error message to send.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.ERROR.value, params=error_message, wait_for_welcome=wait_for_welcome)

    def cmd_help(self, wait_for_welcome=True):
        """
        Requests the server help file.
        This command is not formally defined in an RFC, but is in use by most major IRC daemons.

        Parameters
        ----------
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.HELP.value, wait_for_welcome=wait_for_welcome)

    def cmd_info(self, target="", wait_for_welcome=True):
        """
        Returns information about the <target> server, or the current server if <target> is omitted.
        Information returned includes the server's version, when it was compiled, the patch level, when it was started,
        and any other information which may be considered to be relevant.

        Parameters
        ----------
        target: str (optional)
            The target server to request information from.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.INFO.value, params=target, wait_for_welcome=wait_for_welcome)

    def cmd_invite(self, nickname, channel, wait_for_welcome=True):
        """
        Invites <nickname> to the channel <channel>. <channel> does not have to exist, but if it does,
        only members of the channel are allowed to invite other clients.
        If the channel mode i is set, only channel operators may invite other clients.

        Parameters
        ----------
        nickname: str
            The nickname of the user to invite.
        channel: str
            The channel to invite the user to.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.INVITE.value, params=nickname + " " + channel, wait_for_welcome=wait_for_welcome)

    def cmd_ison(self, nicknames, wait_for_welcome=True):
        """
        Queries the server to see if the clients in the list <nicknames> are currently on the network.
        The server returns only the nicknames that are on the network in a list.
        If none of the clients are on the network, the server returns an empty list.

        Parameters
        ----------
        nicknames: list
            A list of nicknames.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.ISON.value,
                          params=" ".join(nick for nick in nicknames), wait_for_welcome=wait_for_welcome)

    def cmd_join(self, channels, wait_for_welcome=True):
        """
        Joins the specified channels.

        Parameters
        ----------
        channels: collections.iterable
            A list of channels, prefixed with '#'
            This method automatically adds a '#' to the channel name if it is absent.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.JOIN.value,
                          params=",".join("#" + channel if channel[0] != '#' else channel for channel in channels),
                          wait_for_welcome=wait_for_welcome)

    def cmd_kick(self, channel, nickname, message="", wait_for_welcome=True):
        """
        Forcibly removes <nickname> from <channel>.
        This command may only be issued by channel operators.

        Parameters
        ----------
        channel: str
            The channel to kick the user from.
        nickname: str
            The nickname of the client to kick from the channel.
        message: str (optional)
            The message to send to the user about being kicked from the channel.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.KICK.value,
                          params=channel + " " + nickname + (" " + message) if message else "",
                          wait_for_welcome=wait_for_welcome)

    def cmd_kill(self, nickname, message, wait_for_welcome=True):
        """
        Forcibly removes <nickname> from the network. This command may only be issued by IRC operators.

        Parameters
        ----------
        nickname: str
            The nickname of the user to remove from the network.
        message: str
            The reason for the kill command, sent to the user.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.KILL.value, params=nickname + " " + message, wait_for_welcome=wait_for_welcome)

    def cmd_knock(self, channel, message="", wait_for_welcome=True):
        """
        Sends a NOTICE to an invitation-only <channel> with an optional <message>, requesting an invite.
        This command is not formally defined by an RFC, but is supported by most major IRC daemons.
        Support is indicated in a RPL_ISUPPORT reply (numeric 005) with the KNOCK keyword.

        Parameters
        ----------
        channel: str
            The channel to send the request to.
        message: str (optional)
            The message to send with the request.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.KNOCK.value, params=channel + (" " + message) if message else "",
                          wait_for_welcome=wait_for_welcome)

    def cmd_links(self, remote_server="", server_mask="", wait_for_welcome=True):
        """
        Lists all server links matching <server mask>, if given, on <remote server>, or the current server if omitted.

        Parameters
        ----------
        remote_server: str (optional)
            The server to check. If omitted, the current server is used.
            Default value is an empty string.
        server_mask: str (optional)
            The mask used to check for server links. Lists all links if omitted.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.LINKS.value, params=(remote_server + " ") if remote_server else "" + server_mask,
                          wait_for_welcome=wait_for_welcome)

    def cmd_list(self, channels=None, server="", wait_for_welcome=True):
        """
        Lists all channels on the server.
        If the list <channels> is given, it will return the channel topics.
        If <server> is given, the command will be forwarded to <server> for evaluation.

        Parameters
        ----------
        channels: list (optional)
            The channels to get the topics from.
            Default value is None.
        server: str (optional)
            The server to send the topic request to.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.LIST.value,
                          params=(",".join(channels) + " ") if channels is not None else "" + server,
                          wait_for_welcome=wait_for_welcome)

    def cmd_lusers(self, mask="", target="", wait_for_welcome=True):
        """
        The LUSERS command is used to get statistics about the size of the IRC network.
        If no parameter is given, the reply will be about the whole net.
        If a <mask> is specified, then the reply will only concern the part of the network
        formed by the servers matching the mask.
        Finally, if the <target> parameter is specified, the request is forwarded
        to that server which will generate the reply.

        Parameters
        ----------
        mask: str (optional)
            The mask used to specify a certain part of the network.
            The default value is an empty string.
        target: str (optional)
            The target server to send the request to.
            The default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.LUSERS.value,
                          params=(mask + " ") if mask else "" + target,wait_for_welcome=wait_for_welcome)

    def cmd_mode_channel(self, channel, flags, params="", wait_for_welcome=True):
        """
        The MODE command is provided so that channel operators may change the characteristics of `their' channel.
        It is also required that servers be able to change channel modes so that channel operators may be created.

        The various modes available for channels are as follows:

            o - give/take channel operator privileges;
            p - private channel flag;
            s - secret channel flag;
            i - invite-only channel flag;
            t - topic settable by channel operator only flag;
            n - no messages to channel from clients on the outside;
            m - moderated channel;
            l - set the user limit to channel;

        When using the 'o' and 'b' options, a restriction on a total of three per mode command has been imposed.

        Parameters
        ----------
        channel: str
            The channel of which the mode is being set.
        flags: str
            The mode flags to set.
        params: str (optional)
            Optional parameters for the command; see RFC for specification.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.MODE.value,
                          params=channel + " " + flags + (" " + params) if params else "",
                          wait_for_welcome=wait_for_welcome)

    def cmd_mode_nickname(self, nickname, flags, params="", wait_for_welcome=True):
        """
        The user MODEs are typically changes which affect either how the
        client is seen by others or what 'extra' messages the client is sent.
        A user MODE command may only be accepted if both the sender of the
        message and the nickname given as a parameter are both the same.

        The available modes are as follows:

            i - marks a users as invisible;
            s - marks a user for receipt of server notices;
            w - user receives wallops;
            o - operator flag.

        Parameter
        ---------
        nickname: str
            The nickname of the user.
        flags: str
            The mode flags to set.
        params: str (optional)
            Optional parameters for the command; see RFC for specification.
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.MODE.value,
                          params=nickname + " " + flags + (" " + params) if params else "",
                          wait_for_welcome=wait_for_welcome)

    def cmd_motd(self, server="", wait_for_welcome=True):
        """
        Returns the message of the day on <server> or the current server if it is omitted.

        Parameters
        ----------
        server: str (optional)
            The server to retrieve the message from, or the current server if omitted.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is False.
        """
        self.send_command(Commands.MOTD.value, params=server, wait_for_welcome=wait_for_welcome)

    def cmd_names(self, channels=None, server=""):
        """
        Returns a list of who is on the comma-separated list of <channels>, by channel name.
        If <channels> is omitted, all users are shown, grouped by channel name with all users who are not on a channel
        being shown as part of channel "*".
        If <server> is specified, the command is sent to <server> for evaluation.

        Parameters
        ----------
        channels: list (optional)
            The channels from which to return the list of user nicks.
            If omitted, all users are returned.
        server: str (optional)
            If <server> is specified, the command is sent to <server> for evaluation.
        """
        self.send_command(Commands.NAMES.value,
                          params=",".join(channel for channel in channels) +
                                 ((" " + server) if server else "") if channels is not None else "")

    # TODO: Stopped here.

    def cmd_nick(self, nick, wait_for_welcome=False):
        """
        Attempts to set the user's nick on the irc server.

        Parameters
        ----------
        nick: str
            The user's nick name.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is False.
        """
        self.__nick = nick
        self.send_command(Commands.NICK.value, params=nick, wait_for_welcome=wait_for_welcome)

    def cmd_privmsg(self, channel_or_user, message, wait_for_welcome=True):
        """
        Send a message to a channel or a user.

        Parameters
        ----------
        channel_or_user: str
            The user or channel to send a message to. If a channel, it must be prefixed with '#'.
        message: str
            The message to send.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.PRIVMSG.value,
                          params=channel_or_user + " :" + message,
                          wait_for_welcome=wait_for_welcome)

    def cmd_user(self, real_name, invisible=False, wait_for_welcome=False):
        """
        Sends the user data to the server. This is done automatically upon calling IRCConnection#connect,
        using IRCConnection#nick as the default for real_name.

        Parameters
        ----------
        real_name: str
            The user's 'real name' which is visible to other members on the irc network.
        invisible: bool (optional)
            If the user wishes to remain invisible to other members on the network, aside from other members in the same
            channel(s).
            Default value is False.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is False.
        """
        self.send_command(Commands.USER.value,
                          params=self.__nick + " " + str(8 if invisible else 0) + " * :" + real_name,
                          wait_for_welcome=wait_for_welcome)

    def cmd_part(self, channels, reason="", wait_for_welcome=True):
        """
        Leaves the specified channels.

        Parameters
        ----------
        channels: collections.iterable
            A list of channels, prefixed with '#'
            This method automatically adds a '#' to the channel name if it is absent.
        reason: str (optional)
            The reason for leaving the channel(s).
            Default value is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.PART.value,
                          params=",".join("#" + channel if channel[0] != '#' else channel for channel in channels) +
                          " :" + reason,
                          wait_for_welcome=wait_for_welcome)

    def cmd_pong(self, message, wait_for_welcome=False):
        """
        Sends a pong message to the server.

        Parameters
        ----------
        message: str
            The argument after "PING" sent from the server.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is False.
        """
        self.send_command(Commands.PONG.value, params=" :" + message, wait_for_welcome=wait_for_welcome)

    def cmd_quit(self, reason="", wait_for_welcome=True):
        """
        Terminates the connection with the server, and sends an optional reason for quitting.

        Parameters
        ----------
        reason: str (optional)
            The reason for terminating the connection.
            Default is an empty string.
        wait_for_welcome: bool (optional)
            True if the command should be queued until the welcome message is received, or False to send it regardless.
            Default value is True.
        """
        self.send_command(Commands.QUIT.value, params=reason, wait_for_welcome=wait_for_welcome)
        self.__welcomed = False
