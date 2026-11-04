"""Diálogos de abrir e salvar arquivos do sistema operacional (via tkinter)."""

import tkinter as tk
from contextlib import contextmanager
from tkinter import filedialog
from typing import Optional

from .Exceptions import StorageError
from .File import TxtFile


class OSInterface:
    """Classe responsável pela conversação entre o software e o sistema operacional, salvando ou importando arquivos."""

    @staticmethod
    @contextmanager
    def _hidden_root():
        """Context manager que cria uma janela tk invisível e a destrói ao sair.

        Yields:
            A janela raiz do tkinter, oculta.
        """
        root = tk.Tk()
        root.withdraw()
        try:
            yield root
        finally:
            root.destroy()

    @classmethod
    def get_txt_content(cls) -> Optional[str]:
        """Pede ao usuário um arquivo TXT e devolve seu conteúdo.

        Returns:
            Conteúdo do arquivo, ou None se o usuário cancelou ou a leitura falhou.
        """
        with cls._hidden_root():
            path = filedialog.askopenfilename(
                title="Selecione o arquivo TXT",
                filetypes=[("Text Files", "*.txt")],
            )
        if not path:
            return None
        try:
            return TxtFile.load(path).text
        except StorageError as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return None

    @classmethod
    def save_txt_content(cls, text: str) -> bool:
        """Pede ao usuário onde salvar e grava o texto em um arquivo TXT.

        Args:
            text: Conteúdo a gravar.

        Returns:
            True se o arquivo foi salvo, False se o usuário cancelou ou houve erro.
        """
        with cls._hidden_root():
            path = filedialog.asksaveasfilename(
                title="Salvar arquivo TXT",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
            )
        if not path:
            return False  # usuário cancelou
        try:
            TxtFile(path, text).write_file()
            return True
        except StorageError as e:
            print(f"Erro ao salvar o arquivo: {e}")
            return False

    @classmethod
    def save_midi_content(cls, midi_object) -> bool:
        """Pede ao usuário onde salvar e grava um arquivo MIDI.

        Args:
            midi_object: Objeto com método save(path), como o MidiFile do mido.

        Returns:
            True se o arquivo foi salvo, False se o usuário cancelou ou houve erro.
        """
        with cls._hidden_root():
            path = filedialog.asksaveasfilename(
                title="Save MIDI file",
                defaultextension=".mid",
                filetypes=[("MIDI Files", "*.mid")],
            )
        if not path:
            return False
        try:
            midi_object.save(path)
            return True
        except Exception as e:
            print(f"Erro ao salvar o arquivo MIDI: {e}")
            return False
