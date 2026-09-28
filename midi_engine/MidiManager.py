class MidiManager:
    def __init__(self, midi_state):
        self.state = midi_state
        self.rules = []

    def text_processing(self, text):
        for char in text:
            for rule in self.rules:
                if rule.match(char):
                    text = rule.apply(char, self.state)
                    break
