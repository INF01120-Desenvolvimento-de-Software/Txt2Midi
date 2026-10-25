from dataclasses import replace

import pygame
from .ScreenState import StartScreen, EditScreen, PlayScreen
from midi_engine.MidiSettings import MidiSettings


class ScreenManager:
    def __init__(self):
        self.shared_text = ""
        self.midi_settings = MidiSettings()
        self.setting_controls = [
            {
                "label": "BPM",
                "minimum": self.midi_settings.min_bpm,
                "maximum": self.midi_settings.max_bpm,
                "value": self.midi_settings.initial_bpm,
                "on_change": self._set_initial_bpm,
            },
        ]

        self.states = {
            "start": StartScreen(self),
            "edit": EditScreen(self),
            "play": PlayScreen(self),
        }
        self.current_state = None

    def _set_initial_bpm(self, bpm: int):
        self.midi_settings = replace(self.midi_settings, initial_bpm=bpm)

    def build_midi_settings(self) -> MidiSettings:
        return self.midi_settings

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
