# prestige_irc

This module is a simple API for IRC networks.

# Installation

## pip

`pip install prestige_irc`

or

`python -m pip install prestige_irc`

## Manually

Clone this repository into your repo, and install `setup.py`:

```python
git clone https://github.com/avahe-kellenberger/prestige_irc.git
cd prestige_irc
python setup.py install
```
You should now be able to import modules, e.g. `from prestige_irc.commands import Commands`

# API Usage

## Creating a connection

Initialize a connection to an IRC network by creating a new `IRCConnection`, and invoking the `connect` function.

```python
irc_connection = IRCConnection("YourBotsNick")
irc_connection.connect(ip_address="irc.freenode.net")
```

## Listeners:

Add message listeners to the `IRCConnection` object.

```python
def receive(msg):
    print(msg.text)

listener = MessageListener(message_filter=lambda msg: msg.command == Commands.PRIVMSG,
                           receive=receive)
irc_connection.add_listener(listener)
```

The above code will accept all `PRIVMSG` commands via the `message_filter`, then print the `text` of the `IRCMessage`.
See `prestige_irc.commands.Commands` for the list of commands, and `prestige_irc.message.IRCMessage` for the message components.

Filters are invoked by `MessageListener#accept`, which is automatically called when an `IRCConnection` receives a message.
This parameter can be excluded or set to `None`, which will cause `MessageListener#accept` to always return `True`.
When this method returns true, `MessageListener#receive` is invoked.

See the code documentation for details.

## Sending messages and IRC commands:

Most commands are supported by the API by default, and are placed in `IRCConnection`.
Commands are prefixed with `cmd_`, such as `cmd_privmsg`, `cmd_join`, and `cmd_kick`.

These preset commands will handle the message formatting that the IRC server requires, with documentation reflecting the RFC.
Commands that are not yet supported by default can be sent manually with `IRCConnection.send_command` and/or `IRCConnection.send`. 
  
# Speculative Updates:
In the future, this module may support every RFC specified IRC command, if it becomes widely requested.
 
