import pygame
from screenState import startScreen, editScreen, playScreen


class screenManager:
    def __init__(self):
        self.states = {
            "start": startScreen(self),
            "edit": editScreen(self),
            "play": playScreen(self),
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

    def draw(self, surface: pygame.Surface):
        if self.current_state is not None:
            self.current_state.draw(surface)
