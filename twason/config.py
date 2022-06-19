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

from . import moderator


class Command:
    name: str
    message: str
    aliases: [str]
    disabled: bool

    def __init__(self, name: str, message: str, aliases: [str] = None, disabled: bool = False):
        self.name = name
        self.message = message
        self.aliases = aliases if aliases is not None else []
        self.disabled = disabled

    @classmethod
    def from_dict(cls, params: dict):
        return Command(
            params.get('name'),
            params['message'],
            params.get('aliases', []),
            params.get('disabled', False)
        )


class TimerStrategy(Enum):
    ROUND_ROBIN = "round-robin"
    SHUFFLE = "shuffle"


class Timer:
    time_between: int
    msgs_between: int
    strategy: TimerStrategy
    pool: [Command]

    def __init__(
        self,
        time_between: int = 10,
        msgs_between: int = 10,
        strategy: TimerStrategy = TimerStrategy.ROUND_ROBIN,
        pool: [Command] = None
     ):
        self.time_between = time_between
        self.msgs_between = msgs_between
        self.strategy = strategy
        self.pool = pool if pool else []

    @classmethod
    def from_dict(cls, param: dict):
        pool = []

        for c in param.get('pool', []):
            command = Command.from_dict(c)
            if not command.disabled:
                pool.append(command)

        return Timer(
            time_between=param.get('between', {}).get('time', 10),
            msgs_between=param.get('between', {}).get('messages', 10),
            strategy=TimerStrategy(param.get('strategy', 'round-robin')),
            pool=pool
        )


class Config:
    channel: str
    nickname: str
    token: str
    command_prefix: str
    commands: [Command]
    timer: Timer
    moderators: [moderator.Moderator]

    def __init__(
        self,
        channel: str,
        nickname: str,
        token: str,
        command_prefix: str,
        commands: [Command],
        timer: Timer,
        moderators: [moderator.Moderator]
    ):
        self.nickname = nickname
        self.channel = channel
        self.token = token
        self.command_prefix = command_prefix
        self.commands = commands
        self.timer = timer
        self.moderators = moderators

    @classmethod
    def from_dict(cls, params: dict, token: str):
        timer = Timer.from_dict(params.get('timer', {}))

        commands_prefix = params.get('command_prefix', '!')
        commands = []

        help_command = Command("help", "Voici les commandes disponibles : ")

        for command in params.get('commands', []):
            command = Command.from_dict(command)

            if command.disabled:
                continue

            commands.append(command)

        for command in timer.pool:
            if command.name is None:
                continue

            commands.append(command)

        moderators = []
        for mod in params.get('moderator', []):
            moderator_config = params['moderator'][mod]
            if mod == 'caps-lock':
                moderators.append(moderator.CapsLockModerator(
                    moderator_config.get("message", "{author}, stop the caps lock!"),
                    cls.parse_decision(moderator_config.get("decision", "delete")),
                    moderator_config.get("duration", None),
                    moderator_config.get("min-size", 5),
                    moderator_config.get("threshold", 50)
                ))
            if mod == 'flood':
                moderators.append(moderator.FloodModerator(
                    moderator_config.get("message", "{author}, stop the flood!"),
                    cls.parse_decision(moderator_config.get("decision", "timeout")),
                    moderator_config.get("duration", None),
                    moderator_config.get("max-word-length", None),
                    moderator_config.get("raid-cooldown", None),
                    moderator_config.get("ignore-hashtags", False),
                    moderator_config.get("max-msg-occurrences", None),
                    moderator_config.get("min-time-between-occurrence", None)
                ))

        # Generate help command
        if params.get('help', True):
            for command in commands:
                help_command.message = "%s %s%s" % (help_command.message, commands_prefix, command.name)

            commands.append(help_command)

        return Config(
            params.get('channel'),
            params.get('nickname'),
            token,
            commands_prefix,
            commands,
            timer,
            moderators
        )

    @classmethod
    def parse_decision(cls, decision_str) -> moderator.ModerationDecision:
        if decision_str == "delete":
            decision = moderator.ModerationDecision.DELETE_MSG
        elif decision_str == "timeout":
            decision = moderator.ModerationDecision.TIMEOUT_USER
        else:
            print("WARNING: %s moderator's decision is invalid, it has been deactivated!")
            decision = moderator.ModerationDecision.ABSTAIN
        return decision

    def find_command(self, command: str) -> Union[None, Command]:
        if not command.startswith(self.command_prefix):
            return None

        command = command[1:]

        for c in self.commands:
            if c.name == command or command in c.aliases:
                return c

        return None


def get_config(file_path: str):
    with open(file_path, 'r') as config_file:
        token = environ['TWITCH_TOKEN']
        return Config.from_dict(json.loads(config_file.read()), token)
