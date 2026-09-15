class textBox:
    def __init__(self):
        char_seq = []

    @property
    def char_seq(self):
        return self._char_seq

    def extract_file_chars(self, current_file):
        if current_file:
            char_seq = list(current_file)
