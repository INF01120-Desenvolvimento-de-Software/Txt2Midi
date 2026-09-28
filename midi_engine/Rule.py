from abc import ABC, abstractmethod


class Rule(ABC):
    @abstractmethod
    def apply(self, char: str, midi_state) -> str:
        pass

    @abstractmethod
    def match(self, char: str) -> bool:
        pass
