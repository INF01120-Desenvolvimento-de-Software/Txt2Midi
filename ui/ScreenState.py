from abc import ABC, abstractmethod
import pygame

from midi_engine.MidiWriter import MidiWriter
from .UiElements import Button, Text, TextBoxUI
from storage.FileController import FileController


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
            "btn_play": Button(
                575,
                525,
                200,
                50,
                "Play",
                36,
                lambda: self.go_to_play_screen(),
            ),
            "txt_input": TextBoxUI(50, 50, 400, 400, 24),
            "btn_home": Button(
                350,
                525,
                200,
                50,
                "Inicio",
                36,
                lambda: self.manager.change_state("start"),
            ),
            "btn_save_txt": Button(
                50,
                25,
                100,
                25,
                "Save TXT file",
                18,
                lambda: self.manager.change_state("start"),
            ),
            "btn_import_txt": Button(
                175,
                25,
                100,
                25,
                "Import TXT file",
                18,
                lambda: self.import_txt_action(),
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

    def import_txt_action(self):
        content = FileController.get_txt_content()

        if content is not None:
            self.elements["txt_input"].set_text(content)

    def go_to_play_screen(self):
        self.manager.shared_text = self.elements["txt_input"].text
        self.manager.change_state("play")


class PlayScreen(ScreenState):
    def __init__(self, manager):
        super().__init__(manager)
        self.elements = {
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
            "btn_generate": Button(
                300, 250, 200, 50, "Gerar MIDI", 36, lambda: self.generate_midi_action()
            ),
            "status_text": Text(400, 320, "Pronto", 32),
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

    def exit(self):
        super().exit()

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, surface: pygame.Surface):
        surface.fill((50, 30, 30))
        super().draw(surface)
