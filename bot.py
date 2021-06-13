#!/usr/bin/env python3

import irc3
import json
from os import environ


TWITCH_IRC_SERVER = "irc.chat.twitch.tv"
TWITCH_IRC_PORT = 6697


class Command:
    name: str
    message: str

    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

    @classmethod
    def from_dict(cls, params: dict):
        return Command(params['name'], params['message'])


class Config:
    channel: str
    nickname: str
    token: str
    commands: [Command]

    def __init__(self, channel: str, nickname: str, token: str, commands: [Command] = None):
        self.nickname = nickname
        self.channel = channel
        self.token = token
        self.commands = commands if commands is not None else []

    @classmethod
    def from_dict(cls, params: dict, token: str):
        commands = []

        for command in params['commands']:
            commands.append(Command.from_dict(command))

        return Config(
            params['channel'],
            params['nickname'],
            token,
            commands
        )


@irc3.plugin
class TwitchBot:
    def __init__(self, bot):
        self.config = get_config()
        self.bot = bot
        self.log = self.bot.log

    def connection_made(self):
        print('connected')

    def server_ready(self):
        print('ready')

    def connection_lost(self):
        print('connection lost')

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_msg(self, target, mask, data, event):
        author_name = mask.split('!')[0]

        for command in self.config.commands:
            print(command.name)
            print('%s ' % data)
            if ('%s ' % data).startswith('!%s ' % command.name):
                self.bot.privmsg(target, command.message)

    @irc3.event(irc3.rfc.JOIN)
    def on_join(self, mask, channel, **kw):
        print('JOINED')
        print(mask)
        print(channel)
        print(kw)


def get_config():
    with open('config.json', 'r') as config_file:
        token = environ['TWITCH_TOKEN']
        return Config.from_dict(json.loads(config_file.read()), token)


def main() -> int:
    config = get_config()
    bot = irc3.IrcBot.from_config({
        'nick': config.nickname,
        'password': config.token,
        'autojoins': ['%s' % config.channel],
        'host': TWITCH_IRC_SERVER,
        'port': TWITCH_IRC_PORT,
        'ssl': True,
        'includes': [__name__]
    })

    bot.run(forever=True)

    return 0


if __name__ == '__main__':
    exit(main())
