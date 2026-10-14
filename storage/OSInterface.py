import tkinter as tk
from contextlib import contextmanager
from tkinter import filedialog
from typing import Optional

from .File import TxtFile


class OSInterface:

    @staticmethod
    @contextmanager
    def _hidden_root():
        root = tk.Tk()
        root.withdraw()
        try:
            yield root
        finally:
            root.destroy()

    @classmethod
    def get_txt_content(cls) -> Optional[str]:
        with cls._hidden_root():
            path = filedialog.askopenfilename(
                title="Selecione o arquivo TXT",
                filetypes=[("Text Files", "*.txt")],
            )
        if not path:
            return None
        try:
            return TxtFile.load(path).text
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return None

    @classmethod
    def save_txt_content(cls, text: str) -> bool:
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
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
            return False