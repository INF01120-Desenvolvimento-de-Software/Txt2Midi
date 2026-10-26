import pygame
from abc import ABC, abstractmethod
from . import Theme
from .TextEditor import TextEditor

TEXTBOX_GAP = 10
GAPS_PER_AXIS = 2


class UIElements(ABC):
    def __init__(self, x, y, size):
        self.visible = False
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(Theme.FONT_NAME, size)

    @abstractmethod
    def draw(self, surface):
        pass


class GradientBackground:
    def __init__(
        self,
        top_color,
        bottom_color=Theme.BACKGROUND_BASE,
        fade_ratio=Theme.GRADIENT_HEIGHT_RATIO,
    ):
        self.top_color = top_color
        self.bottom_color = bottom_color
        self.fade_ratio = fade_ratio
        self._cached_surface = None

    def draw(self, surface):
        size = surface.get_size()
        if self._cached_surface is None or self._cached_surface.get_size() != size:
            self._cached_surface = self._build(size)
        surface.blit(self._cached_surface, (0, 0))

    def _build(self, size):
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
    def __init__(self, x, y, text, size, color=Theme.TEXT_PRIMARY):
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
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_triggered = action_triggered
        self.style = style

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                self.action_triggered()

    def draw(self, surface):
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

    def __init__(self, x, y, width, text, size, minimum, maximum, value, on_change):
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
        new_value = max(self.minimum, min(self.maximum, round(new_value)))
        if new_value != self.value:
            self.value = new_value
            self.on_change(new_value)

    def reset(self):
        self.set_value(self.default)

    def handle_event(self, event):
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
    def __init__(self, x, y, width, height, size):
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
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

    def set_text(self, imported_text):
        self.editor.set_text(imported_text)

    def handle_event(self, event):
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
        if not self.visible:
            return

        self._draw_background(surface)
        self._draw_text(surface)

        if self.active:
            self._draw_cursor(surface)

    def _draw_background(self, surface):
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

    def _draw_text(self, surface):
        line_height = self.font.get_height()
        text = self.editor.text

        for row, (start, end) in enumerate(self.editor.rows):
            top = self.rect.y + TEXTBOX_GAP + row * line_height
            if top + line_height > self.rect.bottom - TEXTBOX_GAP:
                break

            text_surf = self.font.render(text[start:end], True, Theme.TEXT_PRIMARY)
            surface.blit(text_surf, (self.rect.x + TEXTBOX_GAP, top))

    def _draw_cursor(self, surface):
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
