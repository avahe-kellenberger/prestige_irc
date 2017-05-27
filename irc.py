import re


class IRC:

    """Static IRC utility class."""

    @staticmethod
    def parse(raw_message):
        # TODO: Learn all parsed sections, update docs.
        """Parses IRC messages and stores them in an array.

        result[2] is the sender.
        result[3] is the message description.
        result[4] is the message sent from the sender.

        """

        return re.split("^(?:[:](\S+) )?(\S+)(?: (?!:)(.+?))?(?: [:](.+))?$", str(raw_message))


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

        # TODO: Find out all parts of an irc message.
        self.raw_message = raw_message
        self.sender = parsed[2]
        self.description = parsed[3]
        self.message = parsed[4]
