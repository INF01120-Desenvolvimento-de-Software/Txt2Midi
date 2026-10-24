import unittest
from mido import tempo2bpm, bpm2tempo
from midi_engine.Rule import Rules
from ui.MidiConstants import (
    NOTE_C,
    NOTE_A,
    NOTE_B,
    MAX_MIDI_NOTE,
    DEFAULT_DURATION,
    MIN_BPM,
    MAX_BPM,
    BPM_STEP,
    DEFAULT_BPM,
    HARPSICHORD,
    PIPE_ORGAN,
    BANDONEON,
    TUBULAR_BELLS,
    AGOGO,
    SEMITONES_PER_OCTAVE,
    BASE_OCTAVE,
    VOLUME_VOICE0,
    DURATION_QUARTER,
    DURATION_SIXTEENTH,
)


class TestRules(unittest.TestCase):
    def setUp(self):
        self.parser = Rules()

    def test_parse_valid_notes(self):
        # Teste exclusivo de notas naturais puras (A-G)
        midi = self.parser.parse_text("A C")
        track = midi.tracks[0]
        note_msgs = [m for m in track if m.type == "note_on" and m.velocity > 0]
        self.assertEqual(len(note_msgs), 2)
        expected_note_a = NOTE_A + (BASE_OCTAVE - 4) * SEMITONES_PER_OCTAVE
        expected_note_c = NOTE_C + (BASE_OCTAVE - 4) * SEMITONES_PER_OCTAVE
        self.assertEqual(note_msgs[0].note, expected_note_a)
        self.assertEqual(note_msgs[1].note, expected_note_c)

    def test_parse_accidentals(self):
        # Teste exclusivo da aplicação de sustenidos (#) e bemóis (b)
        midi = self.parser.parse_text("C# Bb")
        track = midi.tracks[0]
        note_msgs = [m for m in track if m.type == "note_on" and m.velocity > 0]
        self.assertEqual(len(note_msgs), 2)
        expected_note_c_sharp = (NOTE_C + 1) + (BASE_OCTAVE - 4) * SEMITONES_PER_OCTAVE
        expected_note_b_flat = (NOTE_A + 1) + (BASE_OCTAVE - 4) * SEMITONES_PER_OCTAVE
        self.assertEqual(note_msgs[0].note, expected_note_c_sharp)
        self.assertEqual(note_msgs[1].note, expected_note_b_flat)

    def test_parse_durations(self):
        # Teste exclusivo da regra de modificação de duração de notas
        midi = self.parser.parse_text("C:3 C:5")
        track = midi.tracks[0]
        off_msgs = [m for m in track if m.type == "note_off"]
        self.assertEqual(len(off_msgs), 2)
        self.assertEqual(off_msgs[0].time, DURATION_QUARTER)
        self.assertEqual(off_msgs[1].time, DURATION_SIXTEENTH)

    def test_multiple_voices_initialization(self):
        # Teste de inicialização de múltiplas vozes independentes
        midi = self.parser.parse_text("A\nB")
        self.assertEqual(len(midi.tracks), 2)
        prog_v0 = [m for m in midi.tracks[0] if m.type == "program_change"][0]
        prog_v1 = [m for m in midi.tracks[1] if m.type == "program_change"][0]
        self.assertEqual(prog_v0.program, HARPSICHORD)
        self.assertEqual(prog_v1.program, PIPE_ORGAN)

    def test_delay_processing(self):
        # Teste de processamento de atraso inicial
        midi = self.parser.parse_text("[4] A")
        track = midi.tracks[0]
        delay_msg = [m for m in track if m.type == "note_on" and m.velocity == 0][0]
        self.assertEqual(delay_msg.time, 4 * DEFAULT_DURATION)

    def test_invalid_character_generates_pause(self):
        # Teste de geração de pausa para caracteres inválidos
        midi = self.parser.parse_text("z")
        track = midi.tracks[0]
        pause_msg = [m for m in track if m.type == "note_on" and m.velocity == 0][-1]
        self.assertEqual(pause_msg.note, NOTE_C)

    def test_bpm_limits(self):
        # Teste dinâmico de limite máximo de BPM
        midi = self.parser.parse_text(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>A")
        track = midi.tracks[0]
        tempos = [m for m in track if m.type == "set_tempo"]
        expected_tempo = bpm2tempo(MAX_BPM)
        self.assertEqual(tempos[-1].tempo, expected_tempo)

    def test_octave_upper_bound_clipping(self):
        # Teste da regra: se passar do limite de oitavas, volta à oitava padrão (offset 0)
        midi = self.parser.parse_text("????????A")
        track = midi.tracks[0]
        note_msg = [m for m in track if m.type == "note_on" and m.velocity > 0][0]
        expected_note = NOTE_A + (BASE_OCTAVE - 4) * SEMITONES_PER_OCTAVE
        self.assertEqual(note_msg.note, expected_note)

    def test_invalid_delay_format_ignored(self):
        # Teste de ignorar formato de atraso inválido
        midi = self.parser.parse_text("[texto] A")
        track = midi.tracks[0]
        note_msgs = [m for m in track if m.type == "note_on" and m.velocity > 0]
        self.assertEqual(len(note_msgs), 1)

    def test_instrument_change_rules(self):
        # Teste dinâmico de mudança de instrumentos por caracteres e dígitos
        midi = self.parser.parse_text("! ; , 2")
        track = midi.tracks[0]
        prog_changes = [m.program for m in track if m.type == "program_change"]
        self.assertEqual(prog_changes[1], BANDONEON)
        self.assertEqual(prog_changes[2], TUBULAR_BELLS)
        self.assertEqual(prog_changes[3], AGOGO)
        expected_digit_instrument = (AGOGO + 2) % 128
        self.assertEqual(prog_changes[4], expected_digit_instrument)

    def test_octave_change_rules(self):
        # Teste de subida e descida de oitava dinâmico
        midi = self.parser.parse_text("C?CVC")
        track = midi.tracks[0]
        notes = [m.note for m in track if m.type == "note_on" and m.velocity > 0]
        self.assertEqual(notes[1], notes[0] + SEMITONES_PER_OCTAVE)
        self.assertEqual(notes[2], notes[0])

    def test_bpm_change_rules(self):
        # Teste de aceleração e desaceleração baseados em constante
        midi = self.parser.parse_text("><")
        track = midi.tracks[0]
        tempos = [round(tempo2bpm(m.tempo)) for m in track if m.type == "set_tempo"]
        self.assertEqual(tempos[1], DEFAULT_BPM + BPM_STEP)
        self.assertEqual(tempos[2], DEFAULT_BPM)

    def test_volume_double_rule(self):
        # Teste da regra de dobrar o volume com limite dinâmico
        midi = self.parser.parse_text(" C")
        track = midi.tracks[0]
        note_msg = [m for m in track if m.type == "note_on" and m.velocity > 0][0]
        expected_volume = min(MAX_MIDI_NOTE, VOLUME_VOICE0 * 2)
        self.assertEqual(note_msg.velocity, expected_volume)

    def test_note_repetition_rule(self):
        # Teste da regra de repetição de nota (vogais/consoantes não mapeadas como 'O')
        midi = self.parser.parse_text("CO")
        track = midi.tracks[0]
        note_msgs = [m for m in track if m.type == "note_on"]
        self.assertEqual(note_msgs[0].velocity, VOLUME_VOICE0)
        self.assertEqual(note_msgs[1].note, note_msgs[0].note)
        self.assertEqual(note_msgs[1].velocity, note_msgs[0].velocity)

    def test_explicit_pause_generation(self):
        # Teste de geração de pausa explícita (letras mapeadas para nulo como 'a')
        midi = self.parser.parse_text("Ca")
        track = midi.tracks[0]
        note_msgs = [m for m in track if m.type == "note_on"]
        self.assertEqual(note_msgs[0].velocity, VOLUME_VOICE0)
        self.assertEqual(note_msgs[1].velocity, 0)


if __name__ == "__main__":
    unittest.main()
