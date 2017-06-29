import re

class IRC:

    """Static IRC utility class."""

    @staticmethod
    def parse(raw_message):
        """Breaks a message from an IRC server into its prefix, command, and arguments.

        Parameters
        ----------
        raw_message: str
            The raw message received from the IRC server.

        Returns
        -------
        TODO
        """

        prefix = ''
        if not raw_message:
            raise Exception("Cannot parse an empty message.")
        if raw_message[0] == ':':
            prefix, raw_message = raw_message[1:].split(' ', 1)
        if raw_message.find(' :') != -1:
            raw_message, trailing = raw_message.split(' :', 1)
            args = raw_message.split()
            args.append(trailing)
        else:
            args = raw_message.split()

        command = args.pop(0)
        return prefix, command, args


class IRCMessage:

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
        parsed = IRC.parse(raw_message)

        self.raw = raw_message
        self.prefix = parsed[0]
        self.command = parsed[1]
        self.args = parsed[2]

    def __str__(self):
        return "Raw: " + self.raw + \
            "\r\nPrefix: " + str(self.prefix) + \
            "\r\nCommand: " + str(self.command) + \
            "\r\nArgs: " + str(self.args)
