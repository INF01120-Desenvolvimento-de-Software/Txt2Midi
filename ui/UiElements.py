import pygame
from abc import ABC, abstractmethod

from . import Theme

TEXTBOX_GAP = 10
GAPS_PER_AXIS = 2
NOT_FOUND = -1


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


class TextBoxUI(UIElements):
    def __init__(self, x, y, width, height, size):
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.lines = []
        self.active = False
        self.cursor_pos = 0

    def set_text(self, imported_text):
        self.text = ""
        self.cursor_pos = 0

        for char in imported_text:
            old_text = self.text
            old_cursor_pos = self.cursor_pos

            self.text += char
            self.cursor_pos += 1

            self._apply_word_wrap()
            self._enforce_height_limit(old_text, old_cursor_pos)

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            self._process_key_event(event)

    def _process_key_event(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._handle_navigation(event.key)
        else:
            old_text = self.text
            old_cursor_pos = self.cursor_pos

            self._handle_typing(event)
            self._apply_word_wrap()
            self._enforce_height_limit(old_text, old_cursor_pos)

    def _handle_navigation(self, key):
        if key == pygame.K_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == pygame.K_RIGHT:
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)

    def _handle_typing(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.text = (
                    self.text[: self.cursor_pos - 1] + self.text[self.cursor_pos :]
                )
                self.cursor_pos -= 1
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.text = (
                self.text[: self.cursor_pos] + "\n" + self.text[self.cursor_pos :]
            )
            self.cursor_pos += 1
        else:
            self.text = (
                self.text[: self.cursor_pos]
                + event.unicode
                + self.text[self.cursor_pos :]
            )
            self.cursor_pos += len(event.unicode)

    def _apply_word_wrap(self):
        if not self.text:
            return

        max_width = self.rect.width - GAPS_PER_AXIS * TEXTBOX_GAP
        lines = self.text.split("\n")
        text_up_to_cursor = self.text[: self.cursor_pos]
        current_line_idx = text_up_to_cursor.count("\n")
        target_line = lines[current_line_idx]

        if self.font.size(target_line)[0] > max_width:
            last_space_idx = target_line.rfind(" ")

            if last_space_idx != NOT_FOUND:
                broken_line = (
                    target_line[:last_space_idx]
                    + "\n"
                    + target_line[last_space_idx + 1 :]
                )
            else:
                broken_line = target_line[:-1] + "\n" + target_line[-1]
                pos_in_line = len(text_up_to_cursor.split("\n")[-1])

                if pos_in_line == len(target_line):
                    self.cursor_pos += 1

            lines[current_line_idx] = broken_line
            self.text = "\n".join(lines)

    def _enforce_height_limit(self, old_text, old_cursor_pos):
        available_height = self.rect.height - (GAPS_PER_AXIS * TEXTBOX_GAP)
        max_lines = available_height // self.font.get_height()
        current_lines = len(self.text.split("\n"))

        if current_lines > max_lines:
            self.text = old_text
            self.cursor_pos = old_cursor_pos

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
        current_y = self.rect.y
        self.lines = self.text.split("\n")

        for line in self.lines:
            if current_y + self.font.get_height() > self.rect.bottom - TEXTBOX_GAP:
                break

            text_surf = self.font.render(line, True, Theme.TEXT_PRIMARY)
            surface.blit(
                text_surf, (self.rect.x + TEXTBOX_GAP, current_y + TEXTBOX_GAP)
            )
            current_y += self.font.get_height()

    def _draw_cursor(self, surface):
        text_up_to_cursor = self.text[: self.cursor_pos]
        lines_before = text_up_to_cursor.split("\n")
        current_line = lines_before[-1]
        line_idx = len(lines_before) - 1

        cursor_x = self.rect.x + TEXTBOX_GAP + self.font.size(current_line)[0]
        cursor_y = self.rect.y + TEXTBOX_GAP + (line_idx * self.font.get_height())

        if cursor_y + self.font.get_height() <= self.rect.bottom - TEXTBOX_GAP:
            blink_phase = pygame.time.get_ticks() % Theme.CURSOR_BLINK_PERIOD_MS
            if blink_phase < Theme.CURSOR_VISIBLE_MS:
                pygame.draw.line(
                    surface,
                    Theme.TEXT_PRIMARY,
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + self.font.get_height()),
                    Theme.CURSOR_WIDTH,
                )
