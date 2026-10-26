from abc import ABC, abstractmethod
import pygame

from midi_engine.Exceptions import (
    InvalidDelayError,
    MidiError,
    MidiLoadError,
    MidiSaveError,
)
from midi_engine.MidiPlayer import MidiPlayer
from midi_engine.MidiWriter import MidiWriter
from midi_engine.MidiConstants import DEFAULT_OUTPUT_FILENAME
from . import Layout, Theme
from .UiElements import Button, GradientBackground, Slider, Text, TextBoxUI
from storage.OSInterface import OSInterface

MIDI_ERROR_MESSAGES = {
    MidiSaveError: "Erro ao salvar!",
    MidiLoadError: "Erro ao carregar!",
    InvalidDelayError: "Atraso inválido!",
}
GENERIC_MIDI_ERROR_MESSAGE = "Erro na geração!"


def message_for_midi_error(error: MidiError) -> str:
    for error_type, message in MIDI_ERROR_MESSAGES.items():
        if isinstance(error, error_type):
            return message
    return GENERIC_MIDI_ERROR_MESSAGE


class ScreenState(ABC):
    def __init__(self, manager, gradient_color=Theme.BACKGROUND_BASE):
        self.elements = {}
        self.manager = manager
        self.background = GradientBackground(gradient_color)

    def enter(self):
        for item in self.elements.values():
            item.visible = True

    def exit(self):
        for item in self.elements.values():
            item.visible = False

    def handle_event(self, event):
        for item in self.elements.values():
            if hasattr(item, "handle_event"):
                item.handle_event(event)

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

    def draw(self, surface: pygame.Surface):
        super().draw(surface)


class EditScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager, Theme.GRADIENT_EDIT)

        self.elements = {
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
            "btn_generate": Button(
                Layout.FOOTER_RIGHT_X,
                Layout.FOOTER_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Gerar",
                Theme.FONT_SIZE_BUTTON,
                lambda: (self.go_to_play_screen()),
                style=Theme.PRIMARY_BUTTON,
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

        self._add_setting_sliders()

    def enter(self):
        super().enter()

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

    def _add_setting_sliders(self):
        for index, control in enumerate(self.manager.setting_controls):
            y = Layout.SLIDER_Y + index * Layout.SLIDER_GAP

            slider = Slider(
                Layout.SLIDER_X,
                y,
                Layout.SLIDER_WIDTH,
                control["label"],
                Theme.FONT_SIZE_BUTTON_SMALL,
                control["minimum"],
                control["maximum"],
                control["value"],
                on_change=control["on_change"],
            )
            self.elements[f"slider_{index}"] = slider

            self.elements[f"btn_reset_{index}"] = Button(
                Layout.SLIDER_X + Layout.SLIDER_WIDTH - Layout.SLIDER_RESET_WIDTH,
                y - 2,
                Layout.SLIDER_RESET_WIDTH,
                Layout.SLIDER_RESET_HEIGHT,
                "Reset",
                Theme.FONT_SIZE_BUTTON_SMALL,
                slider.reset,
                style=Theme.SECONDARY_BUTTON,
            )


class PlayScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager, Theme.GRADIENT_PLAY)
        self.writer = None
        self.elements = {
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
            "btn_edit": Button(
                Layout.FOOTER_RIGHT_X,
                Layout.FOOTER_Y,
                Layout.BUTTON_WIDTH,
                Layout.BUTTON_HEIGHT,
                "Editar",
                Theme.FONT_SIZE_BUTTON,
                lambda: self.manager.change_state("edit"),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_reset": Button(
                Layout.PLAYER_RESET_X,
                Layout.PLAYER_Y,
                Layout.PLAYER_BUTTON_WIDTH,
                Layout.PLAYER_BUTTON_HEIGHT,
                "Reset",
                Theme.FONT_SIZE_PLAYER,
                lambda: MidiPlayer.reset_audio(),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_play": Button(
                Layout.PLAYER_PLAY_X,
                Layout.PLAYER_Y,
                Layout.PLAYER_BUTTON_WIDTH,
                Layout.PLAYER_BUTTON_HEIGHT,
                "Play",
                Theme.FONT_SIZE_PLAYER,
                lambda: MidiPlayer.play_audio(),
                style=Theme.PRIMARY_BUTTON,
            ),
            "btn_pause": Button(
                Layout.PLAYER_PAUSE_X,
                Layout.PLAYER_Y,
                Layout.PLAYER_BUTTON_WIDTH,
                Layout.PLAYER_BUTTON_HEIGHT,
                "Pause",
                Theme.FONT_SIZE_PLAYER,
                lambda: MidiPlayer.pause_audio(),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_export_midi": Button(
                Layout.EXPORT_MIDI_BUTTON_X,
                Layout.EXPORT_MIDI_BUTTON_Y,
                Layout.EXPORT_MIDI_BUTTON_WIDTH,
                Layout.EXPORT_MIDI_BUTTON_HEIGHT,
                "Save Midi",
                Theme.FONT_SIZE_PLAYER,
                lambda: self.export_midi_action(),
                style=Theme.SECONDARY_BUTTON,
            ),
            "status_text": Text(
                Layout.STATUS_TEXT_X,
                Layout.STATUS_TEXT_Y,
                "",
                Theme.FONT_SIZE_STATUS,
                color=Theme.TEXT_SECONDARY,
            ),
        }

    def _show_status(self, message, color):
        self.elements["status_text"].text = message
        self.elements["status_text"].color = color

    def generate_midi_action(self):
        self.writer = (
            None  # Garantindo que o MIDI anterior seja apagado antes de gerar o novo
        )
        text_to_convert = self.manager.shared_text
        if not text_to_convert.strip():
            self._show_status("Texto vazio!", Theme.RED)
            return

        try:
            self.writer = MidiWriter(self.manager.build_midi_settings())
            self.writer.process_text(text_to_convert)
            self.writer.save_midi(DEFAULT_OUTPUT_FILENAME)
            MidiPlayer.load_midi(DEFAULT_OUTPUT_FILENAME)
        except MidiError as error:
            self._show_status(message_for_midi_error(error), Theme.RED)
            return

        self._show_status("Arquivo Gerado!", Theme.GREEN)

    def export_midi_action(self):
        if not self.writer or not self.writer.midi:
            self._show_status("Nenhum MIDI gerado!", Theme.RED)
            return

        if OSInterface.save_midi_content(self.writer.midi):
            self._show_status("MIDI exportado!", Theme.GREEN)
        else:
            self._show_status("Exportação cancelada", Theme.TEXT_SECONDARY)

    def enter(self):
        super().enter()
        self.generate_midi_action()

    def exit(self):
        super().exit()
        self.elements["status_text"].text = ""
        MidiPlayer.stop_audio()

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
