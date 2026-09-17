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


class textBox_UI(uiElements):
    def __init__(self, x, y, width, height, size):
        super().__init__(x, y, size)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.linhas = []
        self.active = False

    def handle_event(self, event):
        if not self.visible:
            return

        largura_maxima = self.rect.width - 2 * TEXTBOX_GAP
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.text += "\n"
            else:
                # podemos colocar um limite de caracteres aqui
                self.text += event.unicode

            lines = self.text.split("\n")
            last_line = lines[-1]

            if self.font.size(last_line)[0] > largura_maxima:
                broke_line = last_line[:-1] + "\n" + last_line[-1]
                lines[-1] = broke_line
                self.text = "\n".join(lines)

    def draw(self, surface):
        if not self.visible:
            return

        current_y = self.rect.y
        self.linhas = self.text.split("\n")
        color = (255, 255, 255) if self.active else (180, 180, 180)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)

        for linha in self.linhas:
            if current_y + self.font.get_height() > self.rect.bottom - TEXTBOX_GAP:
                break

            text_surf = self.font.render(linha, True, (255, 255, 255))
            surface.blit(
                text_surf, (self.rect.x + TEXTBOX_GAP, current_y + TEXTBOX_GAP)
            )
            current_y += self.font.get_height()
