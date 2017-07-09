# prestige.irc

NOTE: Currently under development.

This module will be a simple IRC connection tool in which users listen and send messages to the server.

-Listeners:
  Users can attach listeners for raw server messages, as well as add filters for irc.IRCMessage objects alike.
  Filters will allow the user to accept and delegate certain message types to different messages.
  
  
-Sending Messages:
  Users will be able to send raw messages to the server, or preset message types (such as IRCConnection.join(channels)).
  These preset messages will handle the message formatting that the IRC server requires.
  
-Speculative Updates:
  In the future, this module may support every RFC specified IRC command, but it's not likely. This is a side project for personal
  use and probably will not be extended in functionaily once it meets my requirements.
  
