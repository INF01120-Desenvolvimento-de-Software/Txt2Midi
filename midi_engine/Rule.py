from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from midi_engine.Exceptions import InvalidDelayError
from midi_engine.MidiSettings import MidiSettings
from midi_engine.MidiConstants import (
    NOTE_A,
    NOTE_B,
    NOTE_C,
    NOTE_D,
    NOTE_E,
    NOTE_F,
    NOTE_G,
    BANDONEON,
    TUBULAR_BELLS,
    BAGPIPES,
    AGOGO,
    PIPE_ORGAN,
    PIANO,
    ACCORDION,
    HARMONICA,
    VIOLIN,
    CELLO,
    CONTRABASS,
    ELETRIC_BASS,
    ELETRIC_GUITAR,
    ACOUSTIC_GUITAR,
    BANJO,
    FLUTE,
    CLARINET,
    SOPRANO_SAX,
    OCARINA,
    TRUMPET,
    TUBA,
    MARIMBA,
    XYLOPHONE,
    KALIMBA,
    SEASHORE,
    STRINGS,
    DURATION_EIGHTH,
    DURATION_HALF,
    DURATION_QUARTER,
    DURATION_SIXTEENTH,
    DURATION_SIXTY_FOURTH,
    DURATION_THIRTY_SECOND,
    DURATION_WHOLE,
    SEMITONES_PER_OCTAVE,
    MAX_MIDI_NOTE,
    MAX_OCTAVE_OFFSET,
)

TEMPO_UP = ">"
TEMPO_DOWN = "<"
TEMPO_MARKERS = (TEMPO_UP, TEMPO_DOWN)


class Rules:

    # Classe responsável pelas regras da escrita do arquivo midi

    def __init__(self, settings: MidiSettings = None):

        self.settings = settings if settings is not None else MidiSettings()

        # Dicionário do mapeamento das notas e acidentes:

        self.notes = {
            "A": NOTE_A,
            "B": NOTE_B,
            "C": NOTE_C,
            "D": NOTE_D,
            "E": NOTE_E,
            "F": NOTE_F,
            "G": NOTE_G,
            "Ab": NOTE_A - 1,
            "A#": NOTE_A + 1,
            "Bb": NOTE_A + 1,
            "B#": NOTE_C + SEMITONES_PER_OCTAVE,
            "Cb": NOTE_B - SEMITONES_PER_OCTAVE,
            "C#": NOTE_C + 1,
            "Db": NOTE_C + 1,
            "D#": NOTE_D + 1,
            "Eb": NOTE_D + 1,
            "E#": NOTE_F,
            "Fb": NOTE_E,
            "F#": NOTE_F + 1,
            "Gb": NOTE_F + 1,
            "G#": NOTE_G + 1,
            "a": None,
            "b": None,
            "c": None,
            "d": None,
            "e": None,
            "f": None,
            "g": None,
            "h": None,
        }

        # Dicionário dos instrumentos:

        self.instruments = {
            "!": BANDONEON,
            ";": TUBULAR_BELLS,
            ",": AGOGO,
            "@": BAGPIPES,
            "$": SEASHORE,
            "%": PIPE_ORGAN,
            "&": PIANO,
            "*": ACCORDION,
            "-": HARMONICA,
            "_": VIOLIN,
            "+": CELLO,
            "=": CONTRABASS,
            "/": ELETRIC_GUITAR,
            "\\": ACOUSTIC_GUITAR,
            "|": ELETRIC_BASS,
            "(": BANJO,
            ")": FLUTE,
            "{": CLARINET,
            "}": SOPRANO_SAX,
            "~": OCARINA,
            "^": TRUMPET,
            "'": TUBA,
            '"': MARIMBA,
            "`": XYLOPHONE,
            ":": KALIMBA,
            "]": STRINGS,
        }

        # Dicionário das durações das notas:

        self.durations = {
            "1": DURATION_WHOLE,
            "2": DURATION_HALF,
            "3": DURATION_QUARTER,
            "4": DURATION_EIGHTH,
            "5": DURATION_SIXTEENTH,
            "6": DURATION_THIRTY_SECOND,
            "7": DURATION_SIXTY_FOURTH,
        }

    def _channel_for_voice(self, voice_number: int) -> int:
        return voice_number % self.settings.voice_count

    def parse_text(self, text: str) -> MidiFile:

        # Método que processa o texto de entrada linha por linha, onde cada uma é uma voz diferente

        midi = MidiFile()
        lines = text.splitlines()
        voice_count = self.settings.voice_count
        voice_lines = [""] * min(len(lines), voice_count)
        line_starts = [set() for _ in voice_lines]

        for line_number, line in enumerate(lines):
            voice_number = line_number % voice_count
            line_starts[voice_number].add(len(voice_lines[voice_number]))
            voice_lines[voice_number] += line

        # Interpretador das linhas como vozes:

        for voice_number, line in enumerate(voice_lines):

            track = MidiTrack()
            midi.tracks.append(track)

            # Cada voz toca em seu próprio canal, senão os program_change se sobrescrevem
            channel = self._channel_for_voice(voice_number)

            initial_velocity = self.settings.volume_for_voice(voice_number)
            valid_note = False

            current_instrument = self.settings.instrument_for_voice(voice_number)
            track.append(
                Message(
                    "program_change",
                    program=current_instrument,
                    time=0,
                    channel=channel,
                )
            )

            duration_note = self.settings.default_duration

            base_octave = self.settings.octave_for_voice(voice_number)
            octave_offset = 0
            last_note = NOTE_C

            i = 0

            # Leitura dos caracteres de cada linha:

            while i < len(line):
                caractere = line[i]

                if caractere == "[" and i in line_starts[voice_number]:
                    end_bracket = line.find("]", i)

                    if end_bracket != -1:
                        delay_text = line[i + 1 : end_bracket]

                        try:
                            delay_beats = int(delay_text)
                        except ValueError as error:
                            raise InvalidDelayError(delay_text) from error

                        if delay_beats < 0:
                            raise InvalidDelayError(delay_text)

                        track.append(
                            Message(
                                "note_on",
                                note=NOTE_C,
                                velocity=0,
                                time=delay_beats * midi.ticks_per_beat,
                                channel=channel,
                            )
                        )

                        i = end_bracket + 1
                        continue

                # Espaço em branco que dobra o volume:

                if caractere == " ":
                    initial_velocity = min(MAX_MIDI_NOTE, initial_velocity * 2)
                    i = i + 1
                    continue

                # Subida de oitava:

                elif caractere == "?" or caractere == ".":
                    octave_offset = octave_offset + SEMITONES_PER_OCTAVE

                    if octave_offset > MAX_OCTAVE_OFFSET:
                        octave_offset = 0
                    valid_note = False
                    i = i + 1

                # Descida de oitava:

                elif caractere == "V":
                    octave_offset = octave_offset - SEMITONES_PER_OCTAVE

                    if octave_offset < -MAX_OCTAVE_OFFSET:
                        octave_offset = -MAX_OCTAVE_OFFSET
                    valid_note = False
                    i = i + 1

                # Acelerar o BPM (global):

                elif caractere == ">":
                    track.append(MetaMessage("marker", text=TEMPO_UP, time=0))
                    valid_note = False
                    i = i + 1

                # Diminuir o BPM (global):

                elif caractere == "<":
                    track.append(MetaMessage("marker", text=TEMPO_DOWN, time=0))
                    valid_note = False
                    i = i + 1

                # Mudança de instrumentos numéricos:

                elif caractere.isdigit():
                    digit = int(caractere)

                    if digit % 2 == 0:
                        current_instrument = (current_instrument + digit) % 128
                    else:
                        current_instrument = TUBULAR_BELLS

                    valid_note = False
                    track.append(
                        Message(
                            "program_change",
                            program=current_instrument,
                            time=0,
                            channel=channel,
                        )
                    )
                    i = i + 1

                # Processamento das notas musicais e as suas durações:

                elif caractere in self.notes:

                    note_key = caractere
                    consumed = 1

                    # Verificar os acidentes musicais (só depois de nota maiúscula):

                    if (
                        caractere.isupper()
                        and i + 1 < len(line)
                        and line[i + 1] in ("#", "b")
                    ):
                        note_key = note_key + line[i + 1]
                        consumed = 2

                    # Verificar a duração da nota:

                    if i + consumed < len(line) and line[i + consumed] == ":":
                        if i + consumed + 1 < len(line):
                            duration_caractere = line[i + consumed + 1]
                            if duration_caractere in self.durations:
                                duration_note = self.durations[duration_caractere]
                                consumed = consumed + 2

                    musical_note = self.notes[note_key]

                    # Tratamento das pausas (pausa não conta como nota anterior):

                    if musical_note is None:
                        valid_note = False
                        track.append(
                            Message(
                                "note_on",
                                note=NOTE_C,
                                velocity=0,
                                time=duration_note,
                                channel=channel,
                            )
                        )
                        i = i + consumed
                        continue

                    # Cálculo final da nota:

                    final_note = (
                        musical_note
                        + octave_offset
                        + (base_octave - 4) * SEMITONES_PER_OCTAVE
                    )

                    final_note = max(0, min(MAX_MIDI_NOTE, final_note))

                    valid_note = True
                    last_note = final_note

                    track.append(
                        Message(
                            "note_on",
                            note=final_note,
                            velocity=initial_velocity,
                            time=0,
                            channel=channel,
                        )
                    )
                    track.append(
                        Message(
                            "note_off",
                            note=final_note,
                            velocity=initial_velocity,
                            time=duration_note,
                            channel=channel,
                        )
                    )

                    i = i + consumed

                # Mudança de instrumentos por caractere:

                elif caractere in self.instruments:
                    instrument = self.instruments[caractere]
                    current_instrument = instrument

                    valid_note = False

                    track.append(
                        Message(
                            "program_change",
                            program=instrument,
                            time=0,
                            channel=channel,
                        )
                    )
                    i = i + 1

                else:
                    if valid_note == True:
                        track.append(
                            Message(
                                "note_on",
                                note=last_note,
                                velocity=initial_velocity,
                                time=0,
                                channel=channel,
                            )
                        )
                        track.append(
                            Message(
                                "note_off",
                                note=last_note,
                                velocity=initial_velocity,
                                time=duration_note,
                                channel=channel,
                            )
                        )
                    else:
                        track.append(
                            Message(
                                "note_on",
                                note=NOTE_C,
                                velocity=0,
                                time=duration_note,
                                channel=channel,
                            )
                        )
                    i = i + 1

        self._build_tempo_track(midi)

        return midi

    def _build_tempo_track(self, midi: MidiFile):
        changes = []

        for track in midi.tracks:
            tick = 0
            for msg in track:
                tick += msg.time
                if msg.type == "marker" and msg.text in TEMPO_MARKERS:
                    changes.append((tick, msg.text))

        changes.sort(key=lambda change: change[0])

        current_bpm = self.settings.initial_bpm
        tempo_track = MidiTrack()
        tempo_track.append(
            MetaMessage("set_tempo", tempo=bpm2tempo(current_bpm), time=0)
        )

        previous_tick = 0
        for tick, direction in changes:
            if direction == TEMPO_UP:
                current_bpm = self.settings.faster_bpm(current_bpm)
            else:
                current_bpm = self.settings.slower_bpm(current_bpm)

            tempo_track.append(
                MetaMessage(
                    "set_tempo",
                    tempo=bpm2tempo(current_bpm),
                    time=tick - previous_tick,
                )
            )
            previous_tick = tick

        for track in midi.tracks:
            track[:] = [
                msg
                for msg in track
                if not (msg.type == "marker" and msg.text in TEMPO_MARKERS)
            ]

        midi.tracks.insert(0, tempo_track)
