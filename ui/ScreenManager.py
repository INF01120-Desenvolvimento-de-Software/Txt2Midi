"""Gerenciador das telas do app e das configurações compartilhadas entre elas."""

from dataclasses import replace

import pygame
from .ScreenState import StartScreen, EditScreen, PlayScreen
from midi_engine.MidiSettings import MidiSettings


class ScreenManager:
    """Controla qual tela está ativa e guarda os dados compartilhados.

    Attributes:
        shared_text: Texto escrito na tela de edição, lido pela tela de reprodução.
        midi_settings: Configurações MIDI atuais.
        setting_controls: Descrição dos sliders exibidos na tela de edição.
        states: Telas disponíveis, indexadas por nome.
        current_state: Tela ativa no momento (None antes do primeiro change_state).
    """

    def __init__(self):
        """Cria as configurações, os controles dos sliders e as três telas."""
        self.shared_text = ""
        self.midi_settings = MidiSettings()
        self.setting_controls = [
            {
                "text": "BPM",
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
        """Atualiza o BPM inicial, criando uma nova cópia das configurações.

        Args:
            bpm: Novo BPM inicial.
        """
        self.midi_settings = replace(self.midi_settings, initial_bpm=bpm)

    def build_midi_settings(self) -> MidiSettings:
        return self.midi_settings

    def change_state(self, state_name: str):
        """Troca a tela ativa, chamando exit() na antiga e enter() na nova.

        Args:
            state_name: Nome da tela ("start", "edit" ou "play"). Nomes
                desconhecidos são ignorados.
        """
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
