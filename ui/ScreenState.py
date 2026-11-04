"""Telas do app (início, edição e reprodução) e a base comum entre elas."""

from abc import ABC
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
    """Traduz uma exceção do motor MIDI em mensagem curta para a tela.

    Args:
        error: Exceção capturada.

    Returns:
        Mensagem do tipo de erro correspondente, ou a mensagem genérica.
    """
    for error_type, message in MIDI_ERROR_MESSAGES.items():
        if isinstance(error, error_type):
            return message
    return GENERIC_MIDI_ERROR_MESSAGE


class ScreenState(ABC):
    """Base das telas: guarda os elementos e repassa eventos e desenho a eles.

    Attributes:
        elements: Elementos da tela, por nome (a ordem define a ordem de desenho).
        manager: ScreenManager dono da tela.
        background: Fundo com degradê da tela.
    """

    def __init__(self, manager, gradient_color=Theme.BACKGROUND_BASE):
        """Inicializa a tela.

        Args:
            manager: ScreenManager dono da tela.
            gradient_color: Cor do topo do degradê de fundo.
        """
        self.elements = {}
        self.manager = manager
        self.background = GradientBackground(gradient_color)

    def enter(self):
        """Chamado ao entrar na tela: torna todos os elementos visíveis."""
        for item in self.elements.values():
            item.visible = True

    def exit(self):
        """Chamado ao sair da tela: esconde todos os elementos."""
        for item in self.elements.values():
            item.visible = False

    def handle_event(self, event):
        """Repassa o evento aos elementos que sabem tratá-lo.

        Args:
            event: Evento do pygame.
        """
        for item in self.elements.values():
            if hasattr(item, "handle_event"):
                item.handle_event(event)

    def draw(self, surface):
        """Desenha o fundo e depois os elementos, na ordem do dicionário.

        Args:
            surface: Superfície pygame onde desenhar.
        """
        self.background.draw(surface)
        for item in self.elements.values():
            if hasattr(item, "draw"):
                item.draw(surface)


class StartScreen(ScreenState):
    def __init__(self, manager):
        """Monta o título e o botão "Começar".

        Args:
            manager: ScreenManager dono da tela.
        """
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
    """Tela de edição do texto, com importação/salvamento de TXT e sliders."""

    def __init__(self, manager):
        """Monta a caixa de texto, os botões, o status e os sliders.

        Args:
            manager: ScreenManager dono da tela.
        """
        super().__init__(manager, Theme.GRADIENT_EDIT)

        self.elements = {
            "txt_input": TextBoxUI(
                Layout.TEXTBOX_X,
                Layout.TEXTBOX_Y,
                Layout.TEXTBOX_WIDTH,
                Layout.TEXTBOX_HEIGHT,
                Theme.FONT_SIZE_TEXTBOX,
                Layout.TEXTBOX_MARGIN_WIDTH,
                self.manager.midi_settings.voice_count,
                "Voz",
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
                "Salvar TXT",
                Theme.FONT_SIZE_BUTTON_SMALL,
                lambda: self.save_txt_action(),
                style=Theme.SECONDARY_BUTTON,
            ),
            "btn_import_txt": Button(
                Layout.IMPORT_BUTTON_X,
                Layout.TOOLBAR_Y,
                Layout.SMALL_BUTTON_WIDTH,
                Layout.SMALL_BUTTON_HEIGHT,
                "Importar TXT",
                Theme.FONT_SIZE_BUTTON_SMALL,
                lambda: self.import_txt_action(),
                style=Theme.SECONDARY_BUTTON,
            ),
            "status_text": Text(
                Layout.EDIT_STATUS_TEXT_X,
                Layout.EDIT_STATUS_TEXT_Y,
                "",
                Theme.FONT_SIZE_BUTTON,
                color=Theme.RED,
            ),
        }

        self._add_setting_sliders()

    def enter(self):
        super().enter()

    def exit(self):
        """Esconde os elementos e limpa a mensagem de status."""
        super().exit()
        self.elements["status_text"].text = ""

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

    def save_txt_action(self):
        """Abre o diálogo para salvar o texto atual em um arquivo TXT."""
        OSInterface.save_txt_content(self.elements["txt_input"].text)

    def import_txt_action(self):
        """Importa um TXT para a caixa de texto e avisa se ele foi cortado."""
        content = OSInterface.get_txt_content()
        if content is None:
            return

        was_cut = self.elements["txt_input"].set_text(content)
        if was_cut:
            self.elements["status_text"].text = "Texto Cortado"
        else:
            self.elements["status_text"].text = ""

    def go_to_play_screen(self):
        """Salva o texto no manager e muda para a tela de reprodução."""
        self.manager.shared_text = self.elements["txt_input"].text
        self.manager.change_state("play")

    def _add_setting_sliders(self):
        """Cria um slider e um botão "Reset" para cada item de setting_controls."""
        for index, control in enumerate(self.manager.setting_controls):
            y = Layout.SLIDER_Y + index * Layout.SLIDER_GAP

            slider = Slider(
                Layout.SLIDER_X,
                y,
                Layout.SLIDER_WIDTH,
                control["text"],
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
    """Tela de reprodução: gera o MIDI ao entrar e oferece controles de áudio.

    Attributes:
        writer: MidiWriter do último MIDI gerado com sucesso (ou None).
    """

    def __init__(self, manager):
        """Monta os botões de navegação, de player e de exportação.

        Args:
            manager: ScreenManager dono da tela.
        """
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
        """Exibe uma mensagem na tela.

        Args:
            message: Texto da mensagem.
            color: Cor RGB do texto.
        """
        self.elements["status_text"].text = message
        self.elements["status_text"].color = color

    def generate_midi_action(self):
        """Gera o MIDI a partir do texto compartilhado, salva e carrega no player.

        Mostra o resultado (sucesso, texto vazio ou erro) na mensagem de status.
        """
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
        """Exporta o MIDI gerado por um diálogo de salvar e mostra o resultado."""
        if not self.writer or not self.writer.midi:
            self._show_status("Nenhum MIDI gerado!", Theme.RED)
            return

        if OSInterface.save_midi_content(self.writer.midi):
            self._show_status("MIDI exportado!", Theme.GREEN)
        else:
            self._show_status("Exportação cancelada", Theme.TEXT_SECONDARY)

    def enter(self):
        """Mostra os elementos e gera o MIDI automaticamente."""
        super().enter()
        self.generate_midi_action()

    def exit(self):
        """Esconde os elementos, limpa o status e para o áudio."""
        super().exit()
        self.elements["status_text"].text = ""
        MidiPlayer.stop_audio()

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
