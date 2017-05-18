import re

from prestige.irc import connection


class IRCConnection(connection.Connection):

    """Creates a connection to an IRC network."""
    
    def __init__(self, server, port, nick):
        super().init(server, port)
        self.nick = nick
        
        if (self.connect()):
            self.send("USER "+ self.nick + " " + self.nick + " " + self.nick + " :prestige.irc bot.\n")
            self.add_listener(lambda data: (self.irc_parser(data)))
        else:
            print("Failed to connect to " + self.server + " at port " + self.port + ".")
            exit()
        
    def irc_parser(self, data):
        """Parses IRC messages and stores them in an array.
        
        result[2] is the sender.
        result[3] is the message description.
        result[4] is the message sent from the sender.
        
        """
        
        return re.split("^(?:[:](\S+) )?(\S+)(?: (?!:)(.+?))?(?: [:](.+))?$", str(data))
            
    def join(self, channels):
            """Joins the specified channels.""" 
            for channel in channels:
                print("Joining " + channel + ".")
                self.send("JOIN "+ channel + "\n")
                
    def set_nick(self, nick):
        """Attempts to set the user's nick on the irc server."""
        self.send("NICK " + self.nick +"\n")
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                