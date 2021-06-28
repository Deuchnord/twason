#!/usr/bin/env python3

# Twason - The KISS Twitch bot
# Copyright (C) 2021  Jérôme Deuchnord
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
