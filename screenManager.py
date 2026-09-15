import pygame
from screenState import startScreen, editScreen, playScreen
import pygame


class screenManager:
    def __init__(self, font):
        self.states = {
            "start": startScreen(self, font),
            "edit": editScreen(self, font),
            "play": playScreen(self, font),
        }
        self.current_state = None

    def change_state(self, state_name: str):
        if state_name not in self.states:
            return

        if self.current_state is not None:
            self.current_state.exit()

        self.current_state = self.states[state_name]

        self.current_state.enter()

    def handle_event(self, event: pygame.event.Event):
        if self.current_state is not None:
            self.current_state.handle_event(event)

    def update(self):
        if self.current_state is not None:
            self.current_state.update()

    def draw(self, surface: pygame.Surface):
        if self.current_state is not None:
            self.current_state.draw(surface)
