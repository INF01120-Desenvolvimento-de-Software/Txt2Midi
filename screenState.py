from abc import ABC, abstractmethod
import pygame
from uiElements import Button, Text, textBox_UI


class screenState(ABC):
    def __init__(self, manager):
        self.elements = {}
        self.manager = manager

    @abstractmethod
    def enter(self):
        for item in self.elements.values():
            item.visible = True

    @abstractmethod
    def exit(self):
        for item in self.elements.values():
            item.visible = False

    @abstractmethod
    def handle_event(self, event):
        for item in self.elements.values():
            if hasattr(item, "handle_event"):
                item.handle_event(event)

    @abstractmethod
    def draw(self, surface):
        for item in self.elements.values():
            if hasattr(item, "draw"):
                item.draw(surface)


class startScreen(screenState):
    def __init__(self, manager):
        super().__init__(manager)

        self.elements = {
            "btn_start": Button(
                300,
                200,
                200,
                50,
                "Começar",
                36,
                lambda: self.manager.change_state("edit"),
            ),
            "title": Text(300, 160, "Txt2Midi", 60),
        }

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        surface.fill((30, 30, 40))
        super().draw(surface)


class editScreen(screenState):
    def __init__(self, manager):
        super().__init__(manager)

        self.elements = {
            "btn_back": Button(
                575,
                525,
                200,
                50,
                "Play",
                36,
                lambda: self.manager.change_state("play"),
            ),
            "txt_input": textBox_UI(50, 50, 400, 400, 24),
            "btn_home": Button(
                350,
                525,
                200,
                50,
                "Inicio",
                36,
                lambda: self.manager.change_state("start"),
            ),
        }

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        surface.fill((40, 50, 40))
        super().draw(surface)


class playScreen(screenState):
    def __init__(self, manager):
        super().__init__(manager)

        self.elements = {
            # DEFINIR OS BUTTONS
            "btn_back": Button(
                575,
                525,
                200,
                50,
                "Voltar",
                36,
                lambda: self.manager.change_state("edit"),
            ),
            "btn_home": Button(
                350,
                525,
                200,
                50,
                "Inicio",
                36,
                lambda: self.manager.change_state("start"),
            ),
        }

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        surface.fill((50, 30, 30))
        super().draw(surface)
