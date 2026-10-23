from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from ui.MidiConstants import (
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
    HARPSICHORD,
    BASSOON,
    PIANO0,
    DURATION_EIGHTH,
    DURATION_HALF,
    DURATION_QUARTER,
    DURATION_SIXTEENTH,
    DURATION_SIXTY_FOURTH,
    DURATION_THIRTY_SECOND,
    DURATION_WHOLE,
    VOLUME_VOICE0,
    VOLUME_VOICE1,
    VOLUME_VOICE2,
    VOLUME_VOICE3,
    DEFAULT_BPM,
    MIN_BPM,
    MAX_BPM,
    BPM_STEP,
    SEMITONES_PER_OCTAVE,
    MAX_MIDI_NOTE,
    MAX_OCTAVE_OFFSET,
    BASE_OCTAVE,
    DEFAULT_DURATION,
    TOTAL_VOICES,
)


class Rules:

    # Classe responsável pelas regras da escrita do arquivo midi

    def __init__(self):

        self.midi = MidiFile()
        self.track = MidiTrack()
        self.midi.tracks.append(self.track)

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
            "B#": NOTE_C,
            "Cb": NOTE_B - 12,
            "C#": NOTE_C + 1,
            "Db": NOTE_C + 1,
            "D#": NOTE_D + 1,
            "Eb": NOTE_D + 1,
            "E#": NOTE_E + 1,
            "Fb": NOTE_E - 1,
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

    def parse_text(self, text: str) -> MidiFile:

        # Método que processa o texto de entrada linha por linha, onde cada uma é uma voz diferente

        midi = MidiFile()
        lines = text.splitlines()

        # Interpretador das linhas como vozes:

        for voice_number, line in enumerate(lines):

            track = MidiTrack()
            midi.tracks.append(track)

            # Definições iniciais:

            default_volume = [
                VOLUME_VOICE0,
                VOLUME_VOICE1,
                VOLUME_VOICE2,
                VOLUME_VOICE3,
            ]

            initial_velocity = default_volume[voice_number % TOTAL_VOICES]
            valid_note = False

            default_instruments = [HARPSICHORD, PIPE_ORGAN, PIANO0, BASSOON]

            current_instrument = default_instruments[voice_number % TOTAL_VOICES]

            track.append(Message("program_change", program=current_instrument, time=0))

            duration_note = DEFAULT_DURATION

            current_bpm = DEFAULT_BPM
            track.append(MetaMessage("set_tempo", tempo=bpm2tempo(current_bpm), time=0))

            base_octave = 6 - (voice_number % TOTAL_VOICES)
            octave_offset = 0
            last_note = NOTE_C

            i = 0

            # Leitura dos caracteres de cada linha:

            while i < len(line):
                caractere = line[i]

                if caractere == "[" and i == 0:
                    end_bracket = line.find("]", i)

                    if end_bracket != -1:
                        try:
                            delay_beats = int(line[i + 1 : end_bracket])
                            track.append(
                                Message(
                                    "note_on",
                                    note=NOTE_C,
                                    velocity=0,
                                    time=delay_beats * DEFAULT_DURATION,
                                )
                            )
                            i = end_bracket + 1
                            continue
                        except ValueError:
                            pass

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

                # Acelerar o BPM:

                elif caractere == ">":
                    current_bpm = min(MAX_BPM, current_bpm + BPM_STEP)
                    track.append(
                        MetaMessage("set_tempo", tempo=bpm2tempo(current_bpm), time=0)
                    )
                    valid_note = False
                    i = i + 1

                # Diminuir o BPM:

                elif caractere == "<":
                    current_bpm = max(MIN_BPM, current_bpm - BPM_STEP)
                    track.append(
                        MetaMessage("set_tempo", tempo=bpm2tempo(current_bpm), time=0)
                    )
                    valid_note = False
                    i = i + 1

                # Mudança de instrumentos:

                elif caractere.isdigit():
                    digit = int(caractere)

                    if digit % 2 == 0:
                        current_instrument = (current_instrument + digit) % 128
                    else:
                        current_instrument = TUBULAR_BELLS

                    valid_note = False
                    track.append(
                        Message("program_change", program=current_instrument, time=0)
                    )
                    i = i + 1

                # Processamento das notas musicais e as suas durações:

                elif caractere in self.notes:

                    note_key = caractere
                    consumed = 1

                    # Verificar os acidentes musicais:

                    if i + 1 < len(line) and line[i + 1] in ("#", "b"):
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

                    # Tratamento das pausas:

                    if musical_note is None:
                        valid_note = True
                        last_note = NOTE_C
                        track.append(
                            Message(
                                "note_on", note=NOTE_C, velocity=0, time=duration_note
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

                    if final_note > MAX_MIDI_NOTE:
                        final_note = MAX_MIDI_NOTE

                    valid_note = True
                    last_note = final_note

                    track.append(
                        Message(
                            "note_on",
                            note=final_note,
                            velocity=initial_velocity,
                            time=0,
                        )
                    )
                    track.append(
                        Message(
                            "note_off",
                            note=final_note,
                            velocity=initial_velocity,
                            time=duration_note,
                        )
                    )

                    octave_offset = 0
                    i = i + consumed

                # Mudança de instrumentos por caractere:

                elif caractere in self.instruments:
                    instrument = self.instruments[caractere]

                    valid_note = False

                    track.append(Message("program_change", program=instrument, time=0))
                    i = i + 1

                else:
                    if valid_note == True:
                        track.append(
                            Message(
                                "note_on",
                                note=last_note,
                                velocity=initial_velocity,
                                time=0,
                            )
                        )
                        track.append(
                            Message(
                                "note_off",
                                note=last_note,
                                velocity=initial_velocity,
                                time=duration_note,
                            )
                        )
                    else:
                        track.append(
                            Message(
                                "note_on", note=NOTE_C, velocity=0, time=duration_note
                            )
                        )
                    i = i + 1

        return midi
