from abc import ABC, abstractmethod
from typing import Any

class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, preferences: dict[str, Any]) -> dict[str, Any]:
        """
        Abstract method to generate a sidequest.
        :param preferences: User preferences for the sidequest.
        :return: A dictionary containing title, description, and reward_xp.
        """
        pass
