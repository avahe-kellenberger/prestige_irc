def parse(raw_message):
    """Breaks a message from an IRC server into components.

    Parameters
    ----------
    raw_message: str
        The raw message received from the IRC server.

    Returns
    -------
    nick: str
        The nick name of the sender.
    host: str
        The host of the IRC message (nick!user@host).
    command: str
        The IRC command.
    target: str
        The target to which the message was sent (usually #channel or nick).
    text: str
        The text sent (the last value in `args`).
    args: list
        The arguments in the IRC message.
    """
    host = ""
    if not raw_message:
        raise Exception("Cannot parse an empty message.")
    if raw_message[0] == ":":
        host, raw_message = raw_message[1:].split(" ", 1)
    if raw_message.find(" :") != -1:
        raw_message, trailing = raw_message.split(" :", 1)
        args = raw_message.split()
        args.append(trailing)
    else:
        args = raw_message.split()

    command = args.pop(0)
    nick = host.split("!", 2)[0] if "!" in host else ""
    target = args[0] if len(args) > 0 else ""
    text = args[-1] if len(args) > 0 else ""
    return nick, host, command, target, text, args


class IRCMessage(object):

    def __init__(self, raw_message):
        """
        Parses the raw string received from the server and
        separates each piece into a field using IRC.parse(raw_message).

        Parameters
        ----------
        raw_message: str
            The raw string received from the server.
        """
        # Parse the raw message.
        self.raw = raw_message
        self.nick, self.host, self.command, self.target, self.text, self.args = parse(raw_message)

    def __str__(self):
        return "Raw: " + self.raw + \
            "\r\nNick: " + str(self.nick) + \
            "\r\nHost: " + str(self.host) + \
            "\r\nCommand: " + str(self.command) + \
            "\r\nTarget: " + str(self.target) + \
            "\r\nText: " + str(self.text) + \
            "\r\nArgs: " + str(self.args)
