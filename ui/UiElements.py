"""Componentes de interface em pygame: texto, botão, slider e caixa de texto."""

import pygame
from abc import ABC, abstractmethod
from . import Theme
from .TextEditor import TextEditor

TEXTBOX_GAP = 10
GAPS_PER_AXIS = 2
MARGIN_GAP = 4


class UIElements(ABC):
    """Base abstrata dos elementos desenháveis, com posição, fonte e visibilidade.

    Attributes:
        visible: Se False, o elemento não desenha nem reage a eventos.
        x: Posição horizontal.
        y: Posição vertical.
        font: Fonte usada pelo elemento.
    """

    def __init__(self, x, y, size):
        """Inicializa o elemento (começa invisível).

        Args:
            x: Posição horizontal.
            y: Posição vertical.
            size: Tamanho da fonte.
        """
        self.visible = False
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(Theme.FONT_NAME, size)

    @abstractmethod
    def draw(self, surface):
        pass


class GradientBackground:
    """Fundo com degradê vertical, guardado em cache enquanto o tamanho não muda."""

    def __init__(
        self,
        top_color,
        bottom_color=Theme.BACKGROUND_BASE,
        fade_ratio=Theme.GRADIENT_HEIGHT_RATIO,
    ):
        """Configura o degradê.

        Args:
            top_color: Cor RGB no topo.
            bottom_color: Cor RGB do restante da tela.
            fade_ratio: Fração da altura em que ocorre a transição.
        """
        self.top_color = top_color
        self.bottom_color = bottom_color
        self.fade_ratio = fade_ratio
        self._cached_surface = None

    def draw(self, surface):
        """Desenha o fundo, recriando o cache se o tamanho da superfície mudou.

        Args:
            surface: Superfície pygame onde desenhar.
        """
        size = surface.get_size()
        if self._cached_surface is None or self._cached_surface.get_size() != size:
            self._cached_surface = self._build(size)
        surface.blit(self._cached_surface, (0, 0))

    def _build(self, size):
        """Constrói a superfície do degradê.

        Args:
            size: Tupla (largura, altura).

        Returns:
            Superfície pronta, com o degradê no topo e a cor base abaixo.
        """
        width, height = size
        gradient = pygame.Surface(size)
        gradient.fill(self.bottom_color)

        fade_height = int(height * self.fade_ratio)
        for y in range(fade_height):
            progress = y / fade_height
            color = tuple(
                int(top + (bottom - top) * progress)
                for top, bottom in zip(self.top_color, self.bottom_color)
            )
            pygame.draw.line(gradient, color, (0, y), (width, y))

        return gradient


class Text(UIElements):
    """Texto de uma linha, centralizado horizontalmente em x."""

    def __init__(self, x, y, text, size, color=Theme.TEXT_PRIMARY):
        """Cria o texto.

        Args:
            x: Centro horizontal do texto.
            y: Topo do texto.
            text: Conteúdo exibido.
            size: Tamanho da fonte.
            color: Cor RGB do texto.
        """
        super().__init__(x, y, size)
        self.text = text
        self.color = color

    def draw(self, surface):
        if not self.visible:
            return

        text_surf = self.font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(midtop=(self.x, self.y))
        surface.blit(text_surf, text_rect)


class Button(UIElements):
    """Botão em formato de pílula, com destaque ao passar o mouse."""

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        size,
        action_triggered,
        style=Theme.PRIMARY_BUTTON,
    ):
        """Cria o botão.

        Args:
            x: Posição horizontal.
            y: Posição vertical.
            width: Largura em pixels.
            height: Altura em pixels.
            text: Texto do botão.
            size: Tamanho da fonte.
            action_triggered: Função chamada, sem argumentos, ao clicar.
            style: ButtonStyle com as cores do botão.
        """
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_triggered = action_triggered
        self.style = style

    def handle_event(self, event):
        """Dispara a ação se houve clique esquerdo dentro do botão.

        Args:
            event: Evento do pygame.
        """
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                self.action_triggered()

    def draw(self, surface):
        """Desenha o botão, usando a cor de hover se o mouse estiver sobre ele.

        Args:
            surface: Superfície pygame onde desenhar.
        """
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = self.style.background_hover if hovered else self.style.background

        radius = int(self.rect.height * Theme.PILL_RADIUS_RATIO)
        pygame.draw.rect(surface, color, self.rect, border_radius=radius)

        text_surf = self.font.render(self.text, True, self.style.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider(UIElements):
    """Controle deslizante horizontal para escolher um valor inteiro."""

    def __init__(self, x, y, width, text, size, minimum, maximum, value, on_change):
        """Cria o slider.

        Args:
            x: Posição horizontal.
            y: Posição vertical do rótulo (a barra fica logo abaixo).
            width: Largura da barra em pixels.
            text: Rótulo exibido junto do valor.
            size: Tamanho da fonte.
            minimum: Menor valor possível.
            maximum: Maior valor possível.
            value: Valor inicial, também usado como padrão no reset.
            on_change: Função chamada com o novo valor quando ele muda.
        """
        super().__init__(x, y, size)
        self.text = text
        self.minimum = minimum
        self.maximum = maximum
        self.value = value
        self.default = value
        self.on_change = on_change
        self.dragging = False

        self.track_rect = pygame.Rect(
            x, y + Theme.SLIDER_TEXT_SPACE, width, Theme.SLIDER_TRACK_HEIGHT
        )
        margin = Theme.SLIDER_KNOB_RADIUS * 2
        self.hit_rect = self.track_rect.inflate(margin, margin)

    def set_value(self, new_value):
        """Define o valor (arredondado e limitado) e avisa se ele mudou.

        Args:
            new_value: Valor desejado, que será ajustado a [minimum, maximum].
        """
        new_value = max(self.minimum, min(self.maximum, round(new_value)))
        if new_value != self.value:
            self.value = new_value
            self.on_change(new_value)

    def reset(self):
        self.set_value(self.default)

    def handle_event(self, event):
        """Trata clique e arrasto do mouse sobre o slider.

        Args:
            event: Evento do pygame.
        """
        if not self.visible:
            self.dragging = False
            return

        is_left = getattr(event, "button", None) == pygame.BUTTON_LEFT

        if event.type == pygame.MOUSEBUTTONDOWN and is_left:
            self.dragging = self.hit_rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and is_left:
            self.dragging = False

        if self.dragging and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            ratio = (event.pos[0] - self.track_rect.left) / self.track_rect.width
            self.set_value(self.minimum + ratio * (self.maximum - self.minimum))

    def draw(self, surface):
        """Desenha barra, bolinha, rótulo com o valor e os limites.

        Args:
            surface: Superfície pygame onde desenhar.
        """
        if not self.visible:
            return

        radius = Theme.SLIDER_TRACK_HEIGHT // 2
        center_y = self.track_rect.centery
        ratio = (self.value - self.minimum) / (self.maximum - self.minimum)
        knob_x = int(self.track_rect.left + ratio * self.track_rect.width)

        # barra de fundo e parte preenchida
        pygame.draw.rect(
            surface, Theme.SURFACE_ELEVATED_HOVER, self.track_rect, border_radius=radius
        )
        filled = pygame.Rect(
            self.track_rect.left,
            self.track_rect.top,
            knob_x - self.track_rect.left,
            self.track_rect.height,
        )
        pygame.draw.rect(surface, Theme.GREEN, filled, border_radius=radius)

        # bolinha
        knob_color = Theme.GREEN_HOVER if self.dragging else Theme.WHITE
        pygame.draw.circle(
            surface, knob_color, (knob_x, center_y), Theme.SLIDER_KNOB_RADIUS
        )

        # rótulo com o valor atual
        text_surf = self.font.render(
            f"{self.text}: {self.value}", True, Theme.TEXT_PRIMARY
        )
        surface.blit(text_surf, (self.x, self.y))

        # limites nas extremidades
        below_y = center_y + Theme.SLIDER_KNOB_RADIUS + 4
        min_surf = self.font.render(str(self.minimum), True, Theme.TEXT_SECONDARY)
        max_surf = self.font.render(str(self.maximum), True, Theme.TEXT_SECONDARY)
        surface.blit(min_surf, (self.track_rect.left, below_y))
        surface.blit(
            max_surf, max_surf.get_rect(topright=(self.track_rect.right, below_y))
        )


class TextBoxUI(UIElements):
    """Caixa de texto multilinha com margem numerada por voz e cursor piscante."""

    def __init__(
        self, x, y, width, height, size, margin_width, index_cycle, index_title
    ):
        """Cria a caixa de texto e o editor interno.

        Args:
            x: Posição horizontal da caixa.
            y: Posição vertical da caixa.
            width: Largura da caixa em pixels.
            height: Altura da caixa em pixels.
            size: Tamanho da fonte do texto.
            margin_width: Largura da margem numerada, à esquerda da caixa.
            index_cycle: Após quantas linhas a numeração da margem recomeça de 0.
            index_title: Título exibido acima da margem.
        """
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.margin_rect = pygame.Rect(
            x - margin_width, y, margin_width - MARGIN_GAP, height
        )
        self.index_cycle = index_cycle
        self.index_title = index_title
        self.index_font = pygame.font.SysFont(
            Theme.FONT_NAME, Theme.FONT_SIZE_BUTTON_SMALL
        )
        self.active = False

        max_lines = (height - GAPS_PER_AXIS * TEXTBOX_GAP) // self.font.get_height()
        self.editor = TextEditor(
            measure_width=lambda line: self.font.size(line)[0],
            max_width=width - GAPS_PER_AXIS * TEXTBOX_GAP,
            max_lines=max_lines,
        )

        self._key_actions = {
            pygame.K_LEFT: lambda e: self.editor.move(-1),
            pygame.K_RIGHT: lambda e: self.editor.move(1),
            pygame.K_BACKSPACE: lambda e: self.editor.backspace(),
            pygame.K_RETURN: lambda e: self.editor.newline(),
            pygame.K_KP_ENTER: lambda e: self.editor.newline(),
        }

    @property
    def text(self):
        return self.editor.text

    def set_text(
        self, imported_text
    ):  # was_cut booleana indicando que o texto foi cortado
        """Substitui o texto da caixa (ex.: ao importar um arquivo).

        Args:
            imported_text: Novo conteúdo.

        Returns:
            True se o texto foi cortado por não caber na caixa.
        """
        return self.editor.set_text(imported_text)

    def handle_event(self, event):
        """Ativa a caixa ao clicar e trata o teclado enquanto ativa.

        Args:
            event: Evento do pygame.
        """
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            action = self._key_actions.get(
                event.key, lambda e: self.editor.insert(e.unicode)
            )
            action(event)

    def draw(self, surface):
        """Desenha fundo, margem, texto e (se ativa) o cursor.

        Args:
            surface: Superfície pygame onde desenhar.
        """
        if not self.visible:
            return

        self._draw_background(surface)
        self._draw_margin(surface)
        self._draw_text(surface)

        if self.active:
            self._draw_cursor(surface)

    def _draw_background(self, surface):
        """Desenha o fundo da caixa, com borda branca quando ativa."""
        radius = Theme.TEXTBOX_BORDER_RADIUS
        pygame.draw.rect(
            surface, Theme.SURFACE_ELEVATED, self.rect, border_radius=radius
        )

        border_color = Theme.WHITE if self.active else Theme.SURFACE_ELEVATED_HOVER
        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            Theme.TEXTBOX_BORDER_WIDTH,
            border_radius=radius,
        )

    def _draw_margin(self, surface):
        """Desenha a margem com o título e o número da voz de cada linha lógica."""
        radius = Theme.TEXTBOX_BORDER_RADIUS
        pygame.draw.rect(
            surface, Theme.SURFACE_ELEVATED, self.margin_rect, border_radius=radius
        )
        pygame.draw.rect(
            surface,
            Theme.SURFACE_ELEVATED_HOVER,
            self.margin_rect,
            Theme.TEXTBOX_BORDER_WIDTH,
            border_radius=radius,
        )

        title_surf = self.index_font.render(self.index_title, True, Theme.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(
            midbottom=(self.margin_rect.centerx, self.margin_rect.top - MARGIN_GAP)
        )
        surface.blit(title_surf, title_rect)

        line_height = self.font.get_height()
        for line_number, row in enumerate(self.editor.line_start_rows()):
            top = self.rect.y + TEXTBOX_GAP + row * line_height
            if top + line_height > self.rect.bottom - TEXTBOX_GAP:
                break

            index_surf = self.index_font.render(
                str(line_number % self.index_cycle), True, Theme.TEXT_SECONDARY
            )
            index_rect = index_surf.get_rect(
                center=(self.margin_rect.centerx, top + line_height // 2)
            )
            surface.blit(index_surf, index_rect)

    def _draw_text(self, surface):
        """Desenha cada linha visual do texto que cabe dentro da caixa."""
        line_height = self.font.get_height()
        text = self.editor.text

        for row, (start, end) in enumerate(self.editor.rows):
            top = self.rect.y + TEXTBOX_GAP + row * line_height
            if top + line_height > self.rect.bottom - TEXTBOX_GAP:
                break

            text_surf = self.font.render(text[start:end], True, Theme.TEXT_PRIMARY)
            surface.blit(text_surf, (self.rect.x + TEXTBOX_GAP, top))

    def _draw_cursor(self, surface):
        """Desenha o cursor piscante na posição atual, se estiver visível na caixa."""
        line_height = self.font.get_height()
        row, text_before_cursor = self.editor.cursor_location()

        cursor_x = self.rect.x + TEXTBOX_GAP + self.font.size(text_before_cursor)[0]
        cursor_y = self.rect.y + TEXTBOX_GAP + row * line_height

        if cursor_y + line_height <= self.rect.bottom - TEXTBOX_GAP:
            blink_phase = pygame.time.get_ticks() % Theme.CURSOR_BLINK_PERIOD_MS
            if blink_phase < Theme.CURSOR_VISIBLE_MS:
                pygame.draw.line(
                    surface,
                    Theme.TEXT_PRIMARY,
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + line_height),
                    Theme.CURSOR_WIDTH,
                )
