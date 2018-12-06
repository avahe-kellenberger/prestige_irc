from prestige_irc.irc_connection import IRCConnection

if __name__ == '__main__':

    rizon_bot = IRCConnection('PrestigeBot')
    rizon_bot.connect('irc.rizon.net')

    mopar_bot = IRCConnection('PrestigeBot')
    mopar_bot.connect('irc.moparisthebest.com')
