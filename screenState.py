from abc import ABC, abstractmethod
import pygame
from uiElements import Button, textBox_UI


class screenState(ABC):
    def __init__(self, manager):
        self.elements = {}
        self.manager = manager

    def update(self):
        """Método padrão de atualização. Pode ser sobrescrito nas telas filhas."""
        pass

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
    def __init__(self, manager, font):
        super().__init__(manager)

        self.elements = {
            # DEFINIR OS BUTTONS
            "btn_play": Button(
                300,
                200,
                200,
                50,
                "Tocar",
                font,
                lambda: self.manager.change_state("play"),
            ),
            "btn_edit": Button(
                300,
                280,
                200,
                50,
                "Editar",
                font,
                lambda: self.manager.change_state("edit"),
            ),
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
    def __init__(self, manager, font):
        super().__init__(manager)

        self.elements = {
            # DEFINIR OS BUTTONS
            "btn_back": Button(
                300,
                400,
                200,
                50,
                "Voltar",
                font,
                lambda: self.manager.change_state("start"),
            )
        }

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def update(self):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill((40, 50, 40))
        super().draw(surface)


class playScreen(screenState):
    def __init__(self, manager, font):
        super().__init__(manager)

        self.elements = {
            # DEFINIR OS BUTTONS
            "btn_back": Button(
                300,
                400,
                200,
                50,
                "Voltar",
                font,
                lambda: self.manager.change_state("start"),
            )
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
