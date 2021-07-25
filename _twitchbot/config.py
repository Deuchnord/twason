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


import json

from os import environ
from enum import Enum
from typing import Union


class Command:
    name: str
    message: str
    aliases: [str]

    def __init__(self, name: str, message: str, aliases: [str] = []):
        self.name = name
        self.message = message
        self.aliases = aliases

    @classmethod
    def from_dict(cls, params: dict):
        return Command(params['name'], params['message'], params.get('aliases', []))


class TimerStrategy(Enum):
    ROUND_ROBIN = "round-robin"
    SHUFFLE = "shuffle"


class Timer:
    time_between: int
    msgs_between: int
    strategy: TimerStrategy
    messages: [str]

    def __init__(
        self,
        time_between: int = 10,
        msgs_between: int = 10,
        strategy: TimerStrategy = TimerStrategy.ROUND_ROBIN,
        messages: [str] = None
     ):
        self.time_between = time_between
        self.msgs_between = msgs_between
        self.strategy = strategy
        self.messages = messages if messages else []

    @classmethod
    def from_dict(cls, param: dict):
        return Timer(
            time_between=param.get('between', {}).get('time', 10),
            msgs_between=param.get('between', {}).get('messages', 10),
            strategy=TimerStrategy(param.get('strategy', 'round-robin')),
            messages=param.get('messages', [])
        )


class Config:
    channel: str
    nickname: str
    token: str
    command_prefix: str
    commands: [Command]
    timer: Timer

    def __init__(
        self,
        channel: str,
        nickname: str,
        token: str,
        command_prefix: str,
        commands: [Command],
        timer: Timer
    ):
        self.nickname = nickname
        self.channel = channel
        self.token = token
        self.command_prefix = command_prefix
        self.commands = commands
        self.timer = timer

    @classmethod
    def from_dict(cls, params: dict, token: str):
        commands_prefix = params.get('command_prefix', '!')
        commands = []

        help_command = Command("help", "Voici les commandes disponibles : ")

        for command in params.get('commands', []):
            commands.append(Command.from_dict(command))
            help_command.message = "%s %s%s" % (help_command.message, commands_prefix, command['name'])

        if params.get('help', True):
            commands.append(help_command)

        return Config(
            params.get('channel'),
            params.get('nickname'),
            token,
            commands_prefix,
            commands,
            Timer.from_dict(params.get('timer', {}))
        )

    def find_command(self, command: str) -> Union[None, Command]:
        if command.startswith(self.command_prefix):
            command = command[1:]

        for c in self.commands:
            if c.name == command or command in c.aliases:
                return c

        return None


def get_config(file_path: str):
    with open(file_path, 'r') as config_file:
        token = environ['TWITCH_TOKEN']
        return Config.from_dict(json.loads(config_file.read()), token)
