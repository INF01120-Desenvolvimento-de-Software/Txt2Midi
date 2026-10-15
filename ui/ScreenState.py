from abc import ABC, abstractmethod
from midi_engine.MidiWriter import MidiWriter
from .UiElements import Button, Text, TextBoxUI
from storage.OSInterface import OSInterface
from audio.MidiPlayer import MidiPlayer
from collections import namedtuple
import pygame

Position = namedtuple("position", ["x", "y"])
Size = namedtuple("size", ["width", "height"])

options_bar_pos = Position(50, 25)
options_bar_gap = 105

player_pos = Position(260, 380)
player_gap = 85
player_button_size = Size(80, 30)
player_font_size = 25

lower_bar_pos = Position(390, 525)
lower_bar_gap = 190
lower_bar_font_size = 34
lower_bar_button_size = Size(180, 50)


class ScreenState(ABC):
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


class StartScreen(ScreenState):
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


class EditScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager)

        self.elements = {
            "txt_input": TextBoxUI(50, 50, 400, 400, 24),
            "btn_home": Button(
                lower_bar_pos.x,
                lower_bar_pos.y,
                lower_bar_button_size.width,
                lower_bar_button_size.height,
                "Inicio",
                lower_bar_font_size,
                lambda: self.manager.change_state("start"),
            ),
            "btn_generate": Button(
                lower_bar_pos.x + lower_bar_gap,
                lower_bar_pos.y,
                lower_bar_button_size.width,
                lower_bar_button_size.height,
                "Gerar",
                lower_bar_font_size,
                lambda: (
                    self.go_to_play_screen(),
                    self.generate_midi_action(),
                    MidiPlayer.load_midi("musica_gerada.mid"),
                ),
            ),
            "btn_save_txt": Button(
                options_bar_pos.x,
                options_bar_pos.y,
                100,
                25,
                "Save TXT file",
                18,
                lambda: self.save_txt_action(),
            ),
            "btn_import_txt": Button(
                options_bar_pos.x + options_bar_gap,
                options_bar_pos.y,
                100,
                25,
                "Import TXT file",
                18,
                lambda: self.import_txt_action(),
            ),
            "status_text": Text(400, 320, "", 32),
        }

    def generate_midi_action(self):
        text_to_convert = self.manager.shared_text
        if not text_to_convert.strip():
            self.elements["status_text"].text = "Texto vazio!"
            return

        try:
            writer = MidiWriter()
            writer.process_text(text_to_convert)
            writer.save_midi("musica_gerada.mid")
            self.elements["status_text"].text = "Arquivo Gerado!"
        except Exception as e:
            self.elements["status_text"].text = f"Erro: {e}"

    def enter(self):
        super().enter()
        self.elements["status_text"].text = ""

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        surface.fill((40, 50, 40))
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
        super().__init__(manager)
        self.elements = {
            "btn_home": Button(
                lower_bar_pos.x,
                lower_bar_pos.y,
                lower_bar_button_size.width,
                lower_bar_button_size.height,
                "Inicio",
                lower_bar_font_size,
                lambda: self.manager.change_state("start"),
            ),
            "btn_edit": Button(
                lower_bar_pos.x + lower_bar_gap,
                lower_bar_pos.y,
                lower_bar_button_size.width,
                lower_bar_button_size.height,
                "Editar",
                lower_bar_font_size,
                lambda: self.manager.change_state("edit"),
            ),
            "btn_reset": Button(
                player_pos.x,
                player_pos.y,
                player_button_size.width,
                player_button_size.height,
                "Reset",
                player_font_size,
                lambda: (MidiPlayer.reset_audio()),
            ),
            "btn_play": Button(
                player_pos.x + player_gap,
                player_pos.y,
                player_button_size.width,
                player_button_size.height,
                "Play",
                player_font_size,
                lambda: (MidiPlayer.play_audio(),),
            ),
            "btn_pause": Button(
                player_pos.x + 2 * player_gap,
                player_pos.y,
                player_button_size.width,
                player_button_size.height,
                "Pause",
                player_font_size,
                lambda: (MidiPlayer.pause_audio(),),
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
