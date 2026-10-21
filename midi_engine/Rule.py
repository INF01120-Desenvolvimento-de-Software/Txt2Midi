from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from ui.MidiConstants import (NOTE_A, NOTE_B, NOTE_C, NOTE_D, NOTE_E, NOTE_F, NOTE_G,
                              BANDONEON, TUBULAR_BELLS, BAGPIPES, AGOGO, PIPE_ORGAN, PIANO,
                              ACCORDION, HARMONICA, VIOLIN, CELLO, CONTRABASS, ELETRIC_BASS,
                              ELETRIC_GUITAR, ACOUSTIC_GUITAR, BANJO, FLUTE, CLARINET, SOPRANO_SAX,
                              OCARINA, TRUMPET, TUBA, MARIMBA, XYLOPHONE, KALIMBA, SEASHORE,
                              DURATION_EIGHTH, DURATION_HALF, DURATION_QUARTER, DURATION_SIXTEENTH, DURATION_SIXTY_FOURTH,
                              DURATION_THIRTY_SECOND, DURATION_WHOLE)

class Rules:

    def __init__(self):

        self.midi = MidiFile()
        self.track = MidiTrack()
        self.midi.tracks.append(self.track)

        self.notes = {
            'A': NOTE_A, 'B': NOTE_B, 'C': NOTE_C, 'D': NOTE_D,
            'E': NOTE_E, 'F': NOTE_F, 'G': NOTE_G, 

            'Ab': NOTE_A - 1, 'A#': NOTE_A + 1, 'Bb': NOTE_A + 1, 'B#': NOTE_C,
            'Cb': NOTE_B - 12, 'C#': NOTE_C + 1, 'Db': NOTE_C + 1, 'D#': NOTE_D + 1,
            'Eb': NOTE_D + 1, 'E#': NOTE_E + 1, 'Fb': NOTE_E - 1, 'F#': NOTE_F + 1,
            'Gb': NOTE_F + 1, 'G#': NOTE_G + 1,

            'a': None, 'b': None,'c': None, 'd': None, 
            'e': None, 'f': None, 'g': None, 'h': None,     
        }

        self.instruments = {
            '!': BANDONEON, 
            'O': BAGPIPES, 'o': BAGPIPES, 'I': BAGPIPES,
            'i': BAGPIPES, 'U': BAGPIPES, 'u': BAGPIPES, 
            ';': TUBULAR_BELLS,
            ',': AGOGO, 
            '\n': SEASHORE, 
            'P': PIPE_ORGAN, 'p': PIANO,
            'X': ACCORDION, 'x': HARMONICA, 
            'J': VIOLIN, 'j': CELLO, 
            'K': CONTRABASS, 'k': ELETRIC_GUITAR, 
            'L': ACOUSTIC_GUITAR, 'l': ELETRIC_BASS, 
            'M': BANJO, 'm': FLUTE, 
            'N': CLARINET, 'n': SOPRANO_SAX, 
            'Q': OCARINA, 'q': TRUMPET, 
            'R': TUBA, 'r': MARIMBA, 
            'S': XYLOPHONE, 's': KALIMBA, 
        }

        self.durations = {
            '1': DURATION_WHOLE, 
            '2': DURATION_HALF, 
            '3': DURATION_QUARTER,
            '4': DURATION_EIGHTH, 
            '5': DURATION_SIXTEENTH, 
            '6': DURATION_THIRTY_SECOND, 
            '7': DURATION_SIXTY_FOURTH
        }

    def parse_text(self, text: str) -> MidiFile:

        midi = MidiFile()
        lines = text.splitlines()

        for voice_number, line in enumerate (lines):

            track = MidiTrack()
            midi.tracks.append(track)

            volumes_iniciais = [100, 80, 60, 40] # Sei que aqui a variável ta com nome em pt-br, 
                                                 # dps vou arrumar é só pra achar mais facil!!

            initial_velocity = volumes_iniciais[voice_number % 4]
            valid_note = False

            instrumentos_iniciais = [24, 20, 0, 70] # Aqui tbm
            
            current_instrument = instrumentos_iniciais[voice_number % 4]

            track.append(Message('program_change', program=current_instrument, time=0))

            duration_note = 480

            current_bpm = 120
            track.append(MetaMessage('set_tempo', tempo=bpm2tempo(current_bpm), time=0))
            
            base_octave = 6 - (voice_number % 4)
            octave_offset = 0
            last_note = 60

            i = 0

            while i < len(line):
                caractere = line[i]

                if caractere == '[' and i == 0:
                    end_bracket = line.find(']', i)

                    if end_bracket != -1:
                        try:
                            delay_beats = int(line[i+1:end_bracket])
                            track.append(Message('note_on', note=60, velocity=0, time=delay_beats * 480))
                            i = end_bracket + 1
                            continue
                        except ValueError:
                            pass
        
                if caractere == ' ':
                    initial_velocity = min(127, initial_velocity * 2)
                    i = i + 1
                    continue

                elif caractere == '?' or caractere == '.':
                    octave_offset = octave_offset + 12

                    if octave_offset > 36:
                        octave_offset = 0
                    valid_note = False
                    i = i + 1

                elif caractere == 'V':
                    octave_offset = octave_offset - 12

                    if octave_offset < -36:
                        octave_offset = -36
                    valid_note = False
                    i = i + 1

                elif caractere == '>':
                    current_bpm = min(300, current_bpm + 10)
                    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(current_bpm), time=0))
                    valid_note = False
                    i = i + 1

                elif caractere == '<':
                    current_bpm = max(20, current_bpm - 10)
                    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(current_bpm), time=0))
                    valid_note = False
                    i = i + 1

                elif caractere.isdigit():
                    digit = int(caractere)

                    if digit % 2 == 0:
                        current_instrument = current_instrument + digit
                    else:
                        current_instrument = 15

                    valid_note = False
                    track.append(Message('program_change', program=current_instrument, time=0))
                    i = i + 1

                elif caractere in self.notes:

                    note_key = caractere
                    consumed = 1

                    if i + 1 < len(line) and line[i + 1] in ('#', 'b'):
                        note_key = note_key + line[i + 1]
                        consumed = 2

                    if i + consumed < len(line) and line[i + consumed] == ':':
                        if i + consumed + 1 < len(line):
                            duration_caractere = line[i + consumed + 1]
                            if duration_caractere in self.durations:
                                duration_note = self.durations[duration_caractere]
                                consumed = consumed + 2

                    musical_note = self.notes[note_key]

                    if musical_note is None:
                        valid_note = True
                        last_note = 60
                        track.append(Message('note_on', note=60, velocity=0, time=duration_note))
                        i = i + consumed
                        continue

                    final_note = musical_note + octave_offset + base_octave * 12

                    if final_note > 127:
                        final_note = 127

                    valid_note = True
                    last_note = final_note

                    track.append(Message('note_on', note=final_note, velocity=initial_velocity, time=0))
                    track.append(Message('note_off', note=final_note, velocity=initial_velocity, time=duration_note))

                    octave_offset = 0
                    i = i + consumed

                elif caractere in self.instruments:
                    instrument = self.instruments[caractere]

                    valid_note = False

                    track.append(Message('program_change', program=instrument, time=0))
                    i = i + 1

                else:
                    if valid_note == True:
                        track.append(Message('note_on', note=last_note, velocity=initial_velocity, time=0))
                        track.append(Message('note_off', note=last_note, velocity=initial_velocity, time=duration_note))
                    else:
                        track.append(Message('note_on', note=60, velocity=0,))
                    i = i + 1

        return midi
