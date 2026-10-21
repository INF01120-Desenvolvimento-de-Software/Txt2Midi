class MidiError(Exception):
    """Base de todas as exceções do pacote midi_engine."""


class MidiSaveError(MidiError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Não foi possível salvar o arquivo MIDI '{path}'.")


class MidiLoadError(MidiError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Não foi possível carregar o arquivo MIDI '{path}'.")