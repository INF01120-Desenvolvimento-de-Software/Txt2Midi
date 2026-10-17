from abc import ABC, abstractmethod
import pygame

from midi_engine.MidiPlayer import MidiPlayer
from midi_engine.MidiWriter import MidiWriter
from ui.MidiConstants import DEFAULT_OUTPUT_FILENAME
from . import Layout, Theme
from .UiElements import Button, GradientBackground, Text, TextBoxUI
from storage.OSInterface import OSInterface


class ScreenState(ABC):
    def __init__(self, manager, gradient_color=Theme.BACKGROUND_BASE):
        self.elements = {}
        self.manager = manager
        self.background = GradientBackground(gradient_color)

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
        self.background.draw(surface)
        for item in self.elements.values():
            if hasattr(item, "draw"):
                item.draw(surface)


class StartScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager, Theme.GRADIENT_START)

        self.elements = {
            "btn_start": Button(
                Layout.START_BUTTON_X,
                Layout.START_BUTTON_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Começar",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.manager.change_state("edit"),
                style=Theme.PRIMARY_BUTTON,
            ),
            "title": Text(
                Layout.START_TITLE_X,
                Layout.START_TITLE_Y,
                "Txt2Midi",
                Theme.FONT_SIZE_TITLE,
            ),
        }

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)


class EditScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager, Theme.GRADIENT_EDIT)

        self.elements = {
            "btn_play": Button(
                Layout.FOOTER_RIGHT_X,
                Layout.FOOTER_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Play",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.go_to_play_screen(),
                style=Theme.PRIMARY_BUTTON,
            ),
            "txt_input": TextBoxUI(
                Layout.TEXTBOX_X,
                Layout.TEXTBOX_Y,
                Layout.TEXTBOX_WIDTH,
                Layout.TEXTBOX_HEIGHT,
                Theme.FONT_SIZE_TEXTBOX,
            ),
            "btn_home": Button(
                Layout.FOOTER_LEFT_X,
                Layout.FOOTER_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Inicio",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.manager.change_state("start"),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_save_txt": Button(
                Layout.SAVE_BUTTON_X,
                Layout.TOOLBAR_Y,
                Layout.SMALL_BUTTON_WIDTH,
                Layout.SMALL_BUTTON_HEIGHT,
                "Save TXT file",
                Theme.FONT_SIZE_BUTTON_SMALL,
                lambda: self.save_txt_action(),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_import_txt": Button(
                Layout.IMPORT_BUTTON_X,
                Layout.TOOLBAR_Y,
                Layout.SMALL_BUTTON_WIDTH,
                Layout.SMALL_BUTTON_HEIGHT,
                "Import TXT file",
                Theme.FONT_SIZE_BUTTON_SMALL,
                lambda: self.import_txt_action(),
                style=Theme.SECONDARY_BUTTON,
            ),
        }

    def enter(self):
        super().enter()

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

    def save_txt_action(self):
        OSInterface.save_txt_content(self.elements["txt_input"].text)

    def import_txt_action(self):
        content = OSInterface.get_txt_content()

        if content is not None:
            self.elements["txt_input"].set_text(content)

    def go_to_play_screen(self):
        self.manager.shared_text = self.elements["txt_input"].text
        self.manager.change_state("play")


class PlayScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager, Theme.GRADIENT_PLAY)

        self._loaded_text = None

        self.elements = {
            "btn_back": Button(
                Layout.FOOTER_RIGHT_X,
                Layout.FOOTER_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Voltar",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.manager.change_state("edit"),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_home": Button(
                Layout.FOOTER_LEFT_X,
                Layout.FOOTER_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Inicio",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.manager.change_state("start"),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_generate": Button(
                Layout.GENERATE_BUTTON_X,
                Layout.GENERATE_BUTTON_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Gerar MIDI",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.generate_midi_action(),
                style=Theme.PRIMARY_BUTTON,
            ),
            "btn_reset": Button(
                Layout.PLAYER_RESET_X,
                Layout.PLAYER_Y,
                Layout.PLAYER_BUTTON_WIDTH,
                Layout.PLAYER_BUTTON_HEIGHT,
                "Reset",
                Theme.FONT_SIZE_PLAYER,
                lambda: self.player_action(MidiPlayer.reset_audio),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_play": Button(
                Layout.PLAYER_PLAY_X,
                Layout.PLAYER_Y,
                Layout.PLAYER_BUTTON_WIDTH,
                Layout.PLAYER_BUTTON_HEIGHT,
                "Play",
                Theme.FONT_SIZE_PLAYER,
                lambda: self.player_action(MidiPlayer.play_audio),
                style=Theme.PRIMARY_BUTTON,
            ),
            "btn_pause": Button(
                Layout.PLAYER_PAUSE_X,
                Layout.PLAYER_Y,
                Layout.PLAYER_BUTTON_WIDTH,
                Layout.PLAYER_BUTTON_HEIGHT,
                "Pause",
                Theme.FONT_SIZE_PLAYER,
                lambda: self.player_action(MidiPlayer.pause_audio),
                style=Theme.SECONDARY_BUTTON,
            ),
            "status_text": Text(
                Layout.STATUS_TEXT_X,
                Layout.STATUS_TEXT_Y,
                "Pronto",
                Theme.FONT_SIZE_STATUS,
                Theme.TEXT_SECONDARY,
            ),
        }

    def generate_midi_action(self):
        text_to_convert = self.manager.shared_text
        if not text_to_convert.strip():
            self._set_status("Texto vazio!", Theme.RED)
            return

        try:
            writer = MidiWriter()
            writer.process_text(text_to_convert)
            writer.save_midi(DEFAULT_OUTPUT_FILENAME)
            MidiPlayer.load_midi(DEFAULT_OUTPUT_FILENAME)
            self._loaded_text = text_to_convert
            self._set_status("Arquivo Gerado!", Theme.GREEN)
        except Exception as e:
            self._set_status(f"Erro: {e}", Theme.RED)

    def player_action(self, command):
        #Executa um comando do player só se o midi carregado for do texto atual
        if self._loaded_text != self.manager.shared_text:
            self._set_status("Gere o MIDI primeiro!", Theme.RED)
            return

        command()

    def _set_status(self, message, color):
        self.elements["status_text"].text = message
        self.elements["status_text"].color = color

    def enter(self):
        super().enter()
        self._set_status("Pronto", Theme.TEXT_SECONDARY)

    def exit(self):
        if self._loaded_text is not None:
            MidiPlayer.reset_audio()
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)