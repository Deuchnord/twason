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


class ModerationDecision(Enum):
    ABSTAIN = -1
    DELETE_MSG = 0
    TIMEOUT_USER = 1


class Moderator(ABC):
    message: str
    decision: ModerationDecision

    def __init__(self, message: str, timeout_duration: Union[None, int]):
        self.message = message
        self.timeout_duration = timeout_duration

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def vote(self, msg) -> ModerationDecision:
        pass


class CapsLockModerator(Moderator):
    def __init__(self, message: str, min_size: int, threshold: int, decision: ModerationDecision, timeout_duration: Union[None, int]):
        super().__init__(message, timeout_duration)

        self.min_size = min_size
        self.threshold = threshold / 100
        self.decision = decision

    def get_name(self) -> str:
        return 'Caps Lock'

    def vote(self, msg: str) -> ModerationDecision:
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
