# irc-api

**NOTE: Currently under development**

This module will be a simple IRC connection tool in which users listen and send messages to the server.

### Listeners:
  Users can attach listeners for server messages, as well as add filters for said message objects.
  Filters will allow the user to accept messages via irc.MessageListener#accept, 
  and should then use connection.MessageListener#receive to handle the messages. See documentation for details.

### Sending Messages:
  Users will be able to send raw messages to the server, 
  or preset command types (such as IRCConnection.cmd_join(channels)).
  These preset commands will handle the message formatting that the IRC server requires, 
  with documentation reflecting the RFC.
  
#### Speculative Updates:
  In the future, this module may support every RFC specified IRC command, but it's not likely. 
  This is a side project for personal use and probably will not be extended in functionality 
  once it meets my requirements.
  
