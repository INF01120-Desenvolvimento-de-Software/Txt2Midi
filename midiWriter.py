from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

class midiWriter:

    def __init__(self):
        self.midi = MidiFile()
        self.track = MidiTrack()
        self.midi.tracks.append(self.track)

        self.notes = {
            'A': 69, 'B': 71, 'C': 60, 'D': 62,
            'E': 64, 'F': 65, 'G': 67, 

            'Ab': 68, 'A#': 70, 'Bb': 70, 'B#': 60,
            'Cb': 71, 'C#': 61, 'Db': 61, 'D#': 63,
            'Eb': 63, 'E#': 65, 'Fb': 64, 'F#': 66,
            'Gb': 66, 'G#': 68,

            'a': None, 'b': None,'c': None, 'd': None, 
            'e': None, 'f': None, 'g': None, 'h': None,     
        }

        self.instruments = {
            '!': 24, 'O': 110, 'o': 110, 'I': 110,
            'i': 110, 'U': 110, 'u': 110, ';': 15,
            ',': 114, '\n': 123
        }

        self.duractions = {
            '1': 1920, '2': 960, '3': 480,
            '4': 240, '5': 120, '6': 60, '7': 30
        }

    def generate_midi(self, text, file_name):

        lines = text.splitlines()

        for voice_number, line in enumerate (lines):

            track = MidiTrack()
            self.midi.tracks.append(track)

            volumes_iniciais = [100, 80, 60, 40] # Sei que aqui a variável ta com nome em pt-br, 
                                                 # dps vou arrumar é só pra achar mais facil!!

            initial_velocity = volumes_iniciais[voice_number % 4]
            valid_note = False

            instrumentos_iniciais = [24, 20, 0, 70] # Aqui tbm
            
            current_instrument = instrumentos_iniciais[voice_number % 4]

            track.append(Message('program_change', program=current_instrument, time=0))

            duraction_note = 480

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
                            duraction_caractere = line[i + consumed + 1]
                            if duraction_caractere in self.duractions:
                                duraction_note = self.duractions[duraction_caractere]
                                consumed = consumed + 2

                    musical_note = self.notes[note_key]

                    if musical_note is None:
                        valid_note = True
                        last_note = 60
                        track.append(Message('note_on', note=60, velocity=0, time=duraction_note))
                        i = i + consumed
                        continue

                    final_note = musical_note + octave_offset + base_octave * 12

                    if final_note > 127:
                        final_note = 127

                    valid_note = True
                    last_note = final_note

                    track.append(Message('note_on', note=final_note, velocity=initial_velocity, time=0))
                    track.append(Message('note_off', note=final_note, velocity=initial_velocity, time=duraction_note))

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
                        track.append(Message('note_off', note=last_note, velocity=initial_velocity, time=duraction_note))
                    else:
                        track.append(Message('note_on', note=60, velocity=0,))
                    i = i + 1


        self.midi.save(f'{file_name}.mid')
        print('Arquivo salvo com sucesso')

if __name__ == '__main__':
    writer = midiWriter()

    palavra_teste = (
        "[4] C#:3 D:3 E:3 F:3 G:3 A:3 B:3\n"
        "A:2 C:2 E:2 ?A:2 V:C:2\n"
        "F:1 G:1 > A:1 < B:1\n"
        "C E G C:1"
    )

    name = input("Digite o nome do arquivo midi: ")

    writer.generate_midi(palavra_teste, name)