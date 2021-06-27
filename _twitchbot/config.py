import json

from os import environ
from enum import Enum


class Command:
    name: str
    message: str

    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

    @classmethod
    def from_dict(cls, params: dict):
        return Command(params['name'], params['message'])


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
        messages: [str] = []
     ):
        self.time_between = time_between
        self.msgs_between = msgs_between
        self.strategy = strategy
        self.messages = messages

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


def get_config():
    with open('config.json', 'r') as config_file:
        token = environ['TWITCH_TOKEN']
        return Config.from_dict(json.loads(config_file.read()), token)