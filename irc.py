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

