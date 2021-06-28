#!/usr/bin/env python3

import argparse
import irc3

from _twitchbot.config import get_config
from _twitchbot import twitchbot


TWITCH_IRC_SERVER = "irc.chat.twitch.tv"
TWITCH_IRC_PORT = 6697


def main() -> int:
    args = get_arguments()

    twitchbot.config = get_config(args.config)
    print(twitchbot.config.timer.messages)
    bot = irc3.IrcBot.from_config({
        'nick': twitchbot.config.nickname,
        'password': twitchbot.config.token,
        'autojoins': [twitchbot.config.channel],
        'host': TWITCH_IRC_SERVER,
        'port': TWITCH_IRC_PORT,
        'ssl': True,
        'includes': [twitchbot.__name__]
    })

    bot.run(forever=True)

    return 0


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=str, default='config.json')

    return parser.parse_args()


if __name__ == '__main__':
    exit(main())
