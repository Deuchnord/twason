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


from abc import ABC, abstractmethod
from enum import Enum
from typing import Union
from datetime import datetime, timedelta

EPOCH = datetime(1970, 1, 1)


class ModerationDecision(Enum):
    ABSTAIN = -1
    DELETE_MSG = 0
    TIMEOUT_USER = 1


class Moderator(ABC):
    message: str
    decision: ModerationDecision

    def __init__(self, message: str, decision: ModerationDecision, timeout_duration: Union[None, int]):
        self.message = message
        self.timeout_duration = timeout_duration
        self.decision = decision

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def vote(self, msg: str, author: str) -> ModerationDecision:
        pass


class CapsLockModerator(Moderator):
    def __init__(
            self,
            message: str,
            decision: ModerationDecision,
            timeout_duration: Union[None, int],
            min_size: int,
            threshold: int
    ):
        super().__init__(message, decision, timeout_duration)

        self.min_size = min_size
        self.threshold = threshold / 100

    def get_name(self) -> str:
        return 'Caps Lock'

    def vote(self, msg: str, author: str) -> ModerationDecision:
        msg = ''.join(filter(str.isalpha, msg))

        if len(msg) < self.min_size:
            return ModerationDecision.ABSTAIN

        n = 0
        for char in msg:
            if char.strip() == '':
                continue
            if char == char.upper():
                n += 1

        if n / len(msg) >= self.threshold:
            return self.decision

        return ModerationDecision.ABSTAIN


class FloodModerator(Moderator):
    def __init__(
            self,
            message: str,
            decision: ModerationDecision,
            timeout_duration: Union[None, int],
            max_word_length: Union[None, int],
            raid_cooldown: Union[None, int],
            ignore_hashtags: bool,
            max_msg_occurrences: Union[None, int],
            min_time_between_occurrence: Union[None, int]
    ):
        super().__init__(message, decision, timeout_duration)
        self.max_word_length = max_word_length
        self.raid_cooldown = raid_cooldown
        self.last_raid = EPOCH
        self.ignore_hashtags = ignore_hashtags
        self.max_msg_occurrences = max_msg_occurrences
        self.min_time_between_occurrence = min_time_between_occurrence
        self.last_msgs = []

    def get_name(self) -> str:
        return 'Flood'

    def vote(self, msg: str, author: str) -> ModerationDecision:
        if self.raid_cooldown is not None and self.last_raid + timedelta(minutes=self.raid_cooldown) > datetime.now():
            return ModerationDecision.ABSTAIN

        if self.max_word_length is not None:
            for word in msg.split(' '):
                if word.startswith('#'):
                    continue
                if len(word) > self.max_word_length:
                    return ModerationDecision.TIMEOUT_USER

        if self.max_msg_occurrences is None or self.min_time_between_occurrence is None:
            return ModerationDecision.ABSTAIN

        clean_msg = None
        for last_msg in self.last_msgs:
            if last_msg['first-occurrence'] + timedelta(seconds=self.min_time_between_occurrence) <= datetime.now():
                clean_msg = last_msg
                break

            if author != last_msg['author'] or msg != last_msg['message']:
                break

            last_msg['occurrences'] += 1
            if last_msg['occurrences'] >= self.max_msg_occurrences:
                return ModerationDecision.TIMEOUT_USER

        if clean_msg is not None:
            self.last_msgs.remove(clean_msg)

        self.last_msgs.append({
            'first-occurrence': datetime.now(),
            'author': author,
            'message': msg,
            'occurrences': 1
        })

        return ModerationDecision.ABSTAIN

    def declare_raid(self):
        self.last_raid = datetime.now()
