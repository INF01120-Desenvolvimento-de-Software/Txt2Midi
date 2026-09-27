from mido import MidiFile, MidiTrack, Message

class midiWriter:

    def __init__(self):
        self.midi = MidiFile()
        self.track = MidiTrack()
        self.midi.tracks.append(self.track)

        self.notes = {
            'A': 69, 'B': 71, 'C': 60, 'D': 62,
            'E': 64, 'F': 65, 'G': 67, 'a': None,
            
            'c': None, 'd': None, 'e': None, 'f': None,
            'g': None, 'h': None,     
        }

        self.instruments = {
            '!': 24, 'O': 110, 'o': 110, 'I': 110,
            'i': 110, 'U': 110, 'u': 110, ';': 15,
            ',': 114
        }

    def generate_midi(self, text, file_name):
        
        for caractere in text:
            if caractere in self.notes:
                musical_note = self.notes[caractere]

                if musical_note is None:
                    self.track.append(Message('note_on', note=60, velocity=0,))
                    continue

                self.track.append(Message('note_on', note=musical_note, velocity=80, time=0))
                self.track.append(Message('note_off', note=musical_note, velocity=80, time=480))

            elif caractere in self.instruments:
                instrument = self.instruments[caractere]

                self.track.append(Message('program_change', program=instrument, time=0))


        self.midi.save(f'{file_name}.mid')
        print('Arquivo salvo com sucesso')

if __name__ == '__main__':
    writer = midiWriter()

    palavra_teste = 'AaOBdCcDfEgFhGhAaBdCcDfEgFhGhAaBdCcDfEgFhGhAaBdCcDfEgFhGh'
    name = input("Digite o nome do arquivo midi: ")

    writer.generate_midi(palavra_teste, name)