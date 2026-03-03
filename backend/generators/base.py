from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method to generate a sidequest.
        :param preferences: User preferences for the sidequest.
        :return: A dictionary containing title, description, and reward_xp.
        """
        pass
