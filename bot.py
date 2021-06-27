#!/usr/bin/env python3

import irc3

from _twitchbot.config import get_config
from _twitchbot import twitchbot


TWITCH_IRC_SERVER = "irc.chat.twitch.tv"
TWITCH_IRC_PORT = 6697


def main() -> int:
    config = get_config()
    print(config.timer.messages)
    bot = irc3.IrcBot.from_config({
        'nick': config.nickname,
        'password': config.token,
        'autojoins': [config.channel],
        'host': TWITCH_IRC_SERVER,
        'port': TWITCH_IRC_PORT,
        'ssl': True,
        'includes': [twitchbot.__name__]
    })

    bot.run(forever=True)

    return 0


if __name__ == '__main__':
    exit(main())
