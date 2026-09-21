import pygame
from abc import ABC, abstractmethod

# CONSTANTES
TEXTBOX_GAP = 10


@abstractmethod
class uiElements(ABC):
    def __init__(self, x, y, size):
        self.visible = False
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(None, size)

    @abstractmethod
    def draw(self, surface):
        pass


class Text(uiElements):
    def __init__(self, x, y, text, size):
        super().__init__(x, y, size)
        self.text = text

    def draw(self, surface):
        if not self.visible:
            return

        half_width = surface.get_width() // 2
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midtop=(half_width, self.y))
        surface.blit(text_surf, text_rect)


class Button(uiElements):
    def __init__(self, x, y, width, height, text, size, action_triggered):
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_triggered = action_triggered

    def handle_event(self, event):
        if not self.visible:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action_triggered()

    def draw(self, surface):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        color = (100, 100, 250) if self.rect.collidepoint(mouse_pos) else (70, 70, 200)

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


import pygame
from abc import ABC, abstractmethod

TEXTBOX_GAP = 10


class UIElements(ABC):
    def __init__(self, x, y, size):
        self.visible = False
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont(None, size)

    @abstractmethod
    def draw(self, surface):
        pass


class Text(UIElements):
    def __init__(self, x, y, text, size):
        super().__init__(x, y, size)
        self.text = text

    def draw(self, surface):
        if not self.visible:
            return

        half_width = surface.get_width() // 2
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midtop=(half_width, self.y))
        surface.blit(text_surf, text_rect)


class Button(UIElements):
    def __init__(self, x, y, width, height, text, size, action_triggered):
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_triggered = action_triggered

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action_triggered()

    def draw(self, surface):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        color = (100, 100, 250) if self.rect.collidepoint(mouse_pos) else (70, 70, 200)

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class textBox_UI(UIElements):
    def __init__(self, x, y, width, height, size):
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.lines = []
        self.active = False
        self.cursor_pos = 0

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
            self._handle_typing(event)
            self._apply_word_wrap()

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

        max_width = self.rect.width - 2 * TEXTBOX_GAP
        lines = self.text.split("\n")
        text_up_to_cursor = self.text[: self.cursor_pos]
        current_line_idx = text_up_to_cursor.count("\n")
        target_line = lines[current_line_idx]

        if self.font.size(target_line)[0] > max_width:
            last_space_idx = target_line.rfind(" ")

            if last_space_idx != -1:
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

    def draw(self, surface):
        if not self.visible:
            return

        self._draw_background(surface)
        self._draw_text(surface)

        if self.active:
            self._draw_cursor(surface)

    def _draw_background(self, surface):
        color = (255, 255, 255) if self.active else (180, 180, 180)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)

    def _draw_text(self, surface):
        current_y = self.rect.y
        self.lines = self.text.split("\n")

        for line in self.lines:
            if current_y + self.font.get_height() > self.rect.bottom - TEXTBOX_GAP:
                break

            text_surf = self.font.render(line, True, (255, 255, 255))
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
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + self.font.get_height()),
                    2,
                )
