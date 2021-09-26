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


import irc3

from . import utils

from .config import TimerStrategy
from .moderator import ModerationDecision, Moderator

from random import shuffle
from datetime import datetime, timedelta

config = None


@irc3.plugin
class TwitchBot:
    def __init__(self, bot: irc3.IrcBot):
        self.config = config
        self.messages_stack = []
        self.bot = bot
        self.log = self.bot.log
        self.last_timer_date = datetime.now()
        self.nb_messages_since_timer = 0

    def connection_made(self):
        print('connected')

    def server_ready(self):
        print('ready')

    def connection_lost(self):
        print('connection lost')

    @staticmethod
    def _parse_variables(in_str: str, **kwargs):
        for key in kwargs:
            value = kwargs[key]
            in_str = in_str.replace('{%s}' % key, value)

        return in_str

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_msg(self, mask: str = None, target: str = None, data: str = None, tags: str = None, **_):
        author = mask.split('!')[0]
        command = self.config.find_command(data.lower().split(' ')[0])
        tags_dict = utils.parse_tags(tags)

        if command is not None:
            print('%s: %s%s' % (author, self.config.command_prefix, command.name))
            self.bot.privmsg(target, self._parse_variables(command.message, author=author))
        elif tags_dict.get('mod') == '0':
            self.moderate(tags_dict, data, author, target)

        self.nb_messages_since_timer += 1
        self.play_timer()

    def play_timer(self):
        if not self.messages_stack:
            print('Filling the timer messages stack in')
            self.messages_stack = self.config.timer.pool.copy()
            if self.config.timer.strategy == TimerStrategy.SHUFFLE:
                print('Shuffle!')
                shuffle(self.messages_stack)

        if self.nb_messages_since_timer < self.config.timer.msgs_between or \
            datetime.now() < self.last_timer_date + timedelta(minutes=self.config.timer.time_between):
            return

        command = self.messages_stack.pop(0)

        print("Timer: %s" % command.message)
        self.bot.privmsg('#%s' % self.config.channel, command.message)

        self.nb_messages_since_timer = 0
        self.last_timer_date = datetime.now()

    def moderate(self, tags: {str: str}, msg: str, author: str, channel: str):
        print(tags)
        def delete_msg(mod: Moderator):
            print("[DELETE (reason: %s)] %s: %s" % (mod.get_name(), author, msg))
            self.bot.privmsg(
                channel,
                "/delete %s" % tags['id']
            )

        def timeout(mod: Moderator):
            print("[TIMEOUT (reason: %s)] %s: %s" % (mod.get_name(), author, msg))
            self.bot.privmsg(
                channel,
                "/timeout %s %d %s" % (
                    author,
                    mod.timeout_duration,
                    self._parse_variables(mod.message, author=author)
                )
            )

        # Ignore emotes-only messages
        if tags.get('emote-only', '0') == '1':
            return

        message_to_moderate = msg

        # Remove emotes from message before moderating
        for emote in tags.get('emotes', '').split('/'):
            if emote == '':
                break

            for indices in emote.split(':')[1].split(','):
                [first, last] = indices.split('-')
                first, last = int(first), int(last)
                if first == 0:
                    message_to_moderate = message_to_moderate[last + 1:]
                else:
                    message_to_moderate = message_to_moderate[:first - 1] + message_to_moderate[last + 1:]

        for moderator in self.config.moderators:
            vote = moderator.vote(message_to_moderate)
            if vote == ModerationDecision.ABSTAIN:
                continue
            if vote == ModerationDecision.DELETE_MSG:
                delete_msg(moderator)
            if vote == ModerationDecision.TIMEOUT_USER:
                timeout(moderator)

            self.bot.privmsg(channel, self._parse_variables(moderator.message, author=author))
            break

    @irc3.event(irc3.rfc.JOIN)
    def on_join(self, mask, channel, **_):
        print('JOINED %s as %s' % (channel, mask))

    @irc3.event(irc3.rfc.CONNECTED)
    def on_connected(self, **_):
        for line in [
            "CAP REQ :twitch.tv/commands",
            "CAP REQ :twitch.tv/tags"
        ]:
            self.bot.send_line(line)

        self.bot.join('#%s' % self.config.channel)
