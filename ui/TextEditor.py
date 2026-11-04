"""Editor de texto multilinha com quebra automática, independente do pygame."""

NOT_FOUND = -1


class TextEditor:
    """Guarda o texto, o cursor e o layout das linhas visuais (rows).

    Attributes:
        text: Conteúdo atual do editor.
        cursor_pos: Posição do cursor, de 0 até len(text).
    """

    def __init__(self, measure_width, max_width, max_lines):
        """Cria o editor.

        Args:
            measure_width: Função que recebe um texto e devolve sua largura em pixels.
            max_width: Largura máxima de uma linha visual, em pixels.
            max_lines: Quantidade máxima de linhas visuais permitidas.
        """
        self.text = ""
        self.cursor_pos = 0
        self._measure_width = measure_width
        self._max_width = max_width
        self._max_lines = max_lines
        self._rows_text = ""
        self._rows = [(0, 0)]

    @property
    def rows(self):
        """list[tuple[int, int]]: Pares (início, fim) de cada linha visual, com cache."""
        if self._rows_text != self.text:
            self._rows = self._layout(self.text)
            self._rows_text = self.text
        return self._rows

    def line_start_rows(self):
        """Retorna os índices das linhas visuais que iniciam uma linha lógica.

        Returns:
            Lista de índices em `rows` onde começa um novo parágrafo (após "\\n").
        """
        return [
            index
            for index, (start, _) in enumerate(self.rows)
            if start == 0 or self.text[start - 1] == "\n"
        ]

    def cursor_location(self):
        """Descobre em qual linha visual o cursor está.

        Returns:
            Tupla (índice da linha visual, texto da linha antes do cursor).
        """
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
        """Insere caracteres imprimíveis na posição do cursor.

        Args:
            chars: Texto a inserir. Caracteres não imprimíveis são descartados.
        """
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
        """Move o cursor, mantendo-o dentro do texto.

        Args:
            delta: Deslocamento em caracteres (negativo para a esquerda).
        """
        self.cursor_pos = max(0, min(len(self.text), self.cursor_pos + delta))

    def set_text(self, new_text):
        """Substitui todo o texto, cortando o que exceder o limite de linhas.

        Args:
            new_text: Novo conteúdo. Quebras de linha são normalizadas para "\\n".

        Returns:
            True se o texto foi cortado por exceder max_lines, False caso contrário.
        """
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
        """Filtra o texto mantendo apenas "\\n" e caracteres imprimíveis."""
        return "".join(c for c in chars if c == "\n" or c.isprintable())

    def _commit(self, new_text, new_cursor):
        """Aplica uma edição apenas se o resultado couber em max_lines.

        Args:
            new_text: Texto resultante da edição.
            new_cursor: Posição do cursor após a edição.
        """
        rows = self._layout(new_text)
        if len(rows) > self._max_lines:
            return

        self.text = new_text
        self.cursor_pos = new_cursor
        self._rows = rows
        self._rows_text = new_text

    def _layout(self, text):
        """Calcula as linhas visuais de um texto, parágrafo por parágrafo.

        Args:
            text: Texto completo, com "\\n" separando os parágrafos.

        Returns:
            Lista de pares (início, fim), em índices do texto completo.
        """
        rows = []
        offset = 0
        for logical_line in text.split("\n"):
            rows.extend(self._wrap(logical_line, offset))
            offset += len(logical_line) + 1  # +1 pelo "\n"
        return rows

    def _wrap(self, line, offset):
        """Quebra um parágrafo em linhas visuais.

        Args:
            line: Texto do parágrafo, sem "\\n".
            offset: Posição do parágrafo dentro do texto completo.

        Returns:
            Lista de pares (início, fim) já somados ao offset.
        """
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
        """Encontra onde termina a linha visual que começa em `start`.

        Args:
            line: Texto do parágrafo.
            start: Índice onde a linha visual começa.

        Returns:
            Índice (exclusivo) do fim da linha visual, quebrando no último
            espaço ou, se a palavra for maior que a caixa, no caractere.
        """
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
