"""Geração e gravação de arquivos MIDI a partir de texto."""

from mido import MidiFile
from midi_engine.Exceptions import MidiSaveError
from midi_engine.MidiConstants import MIDI_EXTENSION
from midi_engine.MidiSettings import MidiSettings
from midi_engine.Rule import Rules


class MidiWriter:
    """Converte texto em MidiFile e o salva em disco.

    Attributes:
        parser: Rules que interpreta o texto.
        midi: MidiFile gerado (None até process_text ser chamado).
    """

    def __init__(self, settings: MidiSettings = None):
        """Cria o escritor.

        Args:
            settings: Configurações MIDI. Se None, usa as padrão.
        """
        self.parser = Rules(settings)
        self.midi: MidiFile = None

    def process_text(self, text: str):
        """Converte o texto em MIDI e guarda o resultado em `midi`.

        Args:
            text: Texto escrito segundo as regras do conversor.

        Raises:
            InvalidDelayError: Se o texto tiver um atraso [n] inválido.
        """
        self.midi = self.parser.parse_text(text)

    def save_midi(self, file_name: str):
        """Salva o MIDI gerado, acrescentando ".mid" se faltar.

        Args:
            file_name: Nome ou caminho do arquivo.

        Raises:
            MidiSaveError: Se não for possível gravar o arquivo.
        """
        if not file_name.endswith(MIDI_EXTENSION):
            file_name = file_name + MIDI_EXTENSION

        try:
            self.midi.save(file_name)
        except OSError as error:
            raise MidiSaveError(file_name) from error

        print(f"Arquivo {file_name} salvo com sucesso")
