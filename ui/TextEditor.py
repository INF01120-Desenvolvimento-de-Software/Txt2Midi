NOT_FOUND = -1


class TextEditor:

    def __init__(self, measure_width, max_width, max_lines):
        self.text = ""
        self.cursor_pos = 0
        self._measure_width = measure_width
        self._max_width = max_width
        self._max_lines = max_lines
        self._rows_text = ""
        self._rows = [(0, 0)]

    @property
    def rows(self):
        if self._rows_text != self.text:
            self._rows = self._layout(self.text)
            self._rows_text = self.text
        return self._rows

    def line_start_rows(self):
        return [
            index
            for index, (start, _) in enumerate(self.rows)
            if start == 0 or self.text[start - 1] == "\n"
        ]

    def cursor_location(self):
        rows = self.rows
        last = len(rows) - 1
        for index, (start, end) in enumerate(rows):
            at_row_end = self.cursor_pos == end and (
                index == last or rows[index + 1][0] != end
            )
            if self.cursor_pos < end or at_row_end:
                return index, self.text[start : self.cursor_pos]
        return last, ""

    def insert(self, chars):
        chars = self._printable(chars)
        if chars:
            self._commit(
                self.text[: self.cursor_pos] + chars + self.text[self.cursor_pos :],
                self.cursor_pos + len(chars),
            )

    def newline(self):
        self.insert("\n")

    def backspace(self):
        if self.cursor_pos > 0:
            self._commit(
                self.text[: self.cursor_pos - 1] + self.text[self.cursor_pos :],
                self.cursor_pos - 1,
            )

    def move(self, delta):
        self.cursor_pos = max(0, min(len(self.text), self.cursor_pos + delta))

    def set_text(self, new_text):
        clean = new_text.replace("\r\n", "\n").replace("\r", "\n")
        clean = self._printable(clean)

        rows = self._layout(clean)
        was_cut = len(rows) > self._max_lines
        if was_cut:
            clean = clean[: rows[self._max_lines - 1][1]]

        self.text = clean
        self.cursor_pos = len(clean)
        return was_cut

    @staticmethod
    def _printable(chars):
        return "".join(c for c in chars if c == "\n" or c.isprintable())

    def _commit(self, new_text, new_cursor):
        rows = self._layout(new_text)
        if len(rows) > self._max_lines:
            return

        self.text = new_text
        self.cursor_pos = new_cursor
        self._rows = rows
        self._rows_text = new_text

    def _layout(self, text):
        rows = []
        offset = 0
        for logical_line in text.split("\n"):
            rows.extend(self._wrap(logical_line, offset))
            offset += len(logical_line) + 1  # +1 pelo "\n"
        return rows

    def _wrap(self, line, offset):
        if not line:
            return [(offset, offset)]

        rows = []
        start = 0
        while start < len(line):
            end = self._fit(line, start)
            rows.append((offset + start, offset + end))
            start = end
        return rows

    def _fit(self, line, start):
        last_space = NOT_FOUND
        pos = start

        while pos < len(line):
            if self._measure_width(line[start : pos + 1].rstrip()) > self._max_width:
                break
            if line[pos] == " ":
                last_space = pos
            pos += 1

        if pos == len(line):
            return pos
        if last_space != NOT_FOUND:
            return last_space + 1  # quebra depois do último espaço
        return max(pos, start + 1)  # palavra maior que a caixa: quebra no caractere
