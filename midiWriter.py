from mido import MidiFile, MidiTrack, Message

class midiWriter:

    def __init__(self):
        self.midi = MidiFile()
        self.track = MidiTrack()
        self.midi.tracks.append(self.track)

        self.notes = {
            'A': 69, 'B': 71, 'C': 60, 'D': 62,
            'E': 64, 'F': 65, 'G': 67, 'H': 72, 
            'a': None, 'b': None,'c': None, 'd': None, 
            'e': None, 'f': None, 'g': None, 'h': None,     
        }

        self.instruments = {
            '!': 24, 'O': 110, 'o': 110, 'I': 110,
            'i': 110, 'U': 110, 'u': 110, ';': 15,
            ',': 114, '\n': 123
        }

    def generate_midi(self, text, file_name):

        initial_velocity = 80
        valid_note = False
        current_instrument = 0
        octave_offset = 0
        last_note = 60
        
        for caractere in text:

            if caractere == ' ':
                initial_velocity = min(127, initial_velocity * 2)
                continue

            elif caractere == '?' or caractere == '.':
                octave_offset = octave_offset + 12

                if octave_offset > 36:
                    octave_offset = 0
                valid_note = False

            elif caractere.isdigit():
                digit = int(caractere)

                if digit % 2 == 0:
                    current_instrument = current_instrument + digit
                else:
                    current_instrument = 15

                valid_note = False
                self.track.append(Message('program_change', program=current_instrument, time=0))

            elif caractere in self.notes:
                musical_note = self.notes[caractere]

                if musical_note is None:
                    valid_note = True
                    last_note = 60
                    self.track.append(Message('note_on', note=60, velocity=0,))
                    continue

                final_note = musical_note + octave_offset
                if final_note > 127:
                    final_note = 127

                valid_note = True
                last_note = final_note

                self.track.append(Message('note_on', note=final_note, velocity=initial_velocity, time=0))
                self.track.append(Message('note_off', note=final_note, velocity=initial_velocity, time=480))

                octave_offset = 0

            elif caractere in self.instruments:
                instrument = self.instruments[caractere]

                valid_note = False

                self.track.append(Message('program_change', program=instrument, time=0))

            else:
                if valid_note == True:
                    self.track.append(Message('note_on', note=last_note, velocity=initial_velocity, time=0))
                    self.track.append(Message('note_off', note=last_note, velocity=initial_velocity, time=480))
                else:
                    self.track.append(Message('note_on', note=60, velocity=0,))


        self.midi.save(f'{file_name}.mid')
        print('Arquivo salvo com sucesso')

if __name__ == '__main__':
    writer = midiWriter()

    palavra_teste = 'AaOBdCcDfEgFhGhAaBdCcDfEgFhGhAaBdCcDfEgFhGhAaBdCcDfEgFhGh'
    name = input("Digite o nome do arquivo midi: ")

    writer.generate_midi(palavra_teste, name)