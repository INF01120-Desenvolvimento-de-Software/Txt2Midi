import pygame
from abc import ABC, abstractmethod

# CONSTANTES
TEXTBOX_GAP = 10


@abstractmethod
class uiElements(ABC):
    def __init__(self, x, y, font):
        self.visible = False
        self.x = x
        self.y = y
        self.font = font

    @abstractmethod
    def draw(self, surface):
        pass


class Text(uiElements):
    def __init__(self, x, y, text, font):
        super().__init__(x, y, font)
        self.text = text

    def draw(self, surface):
        if not self.visible:
            return

        half_width = surface.get_width() // 2
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midtop=(half_width, self.y))
        surface.blit(text_surf, text_rect)


class Button(uiElements):
    def __init__(self, x, y, width, height, text, font, action_triggered):
        super().__init__(x, y, font)
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
    def __init__(self, x, y, width, height, font):
        super().__init__(x, y, font)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == (pygame.KEYDOWN or pygame.ISDOWN) and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # podemos colocar um limite de caracteres aqui
                self.text += event.unicode

    def draw(self, surface):  # TRATAR DO CASO DE QUEBRA DE LINHA
        if not self.visible:
            return
        color = (255, 255, 255) if self.active else (180, 180, 180)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + TEXTBOX_GAP, self.rect.y + TEXTBOX_GAP))
