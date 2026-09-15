import pygame

# CONSTANTES
TEXTBOX_GAP = 10


class Button:
    def __init__(self, x, y, width, height, text, font, action_triggered):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action_triggered = action_triggered
        self.visible = False

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


class textBox_UI:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = font
        self.active = False
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
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
        surface.blit(text_surf, self.rect.x + TEXTBOX_GAP, self.rect.y + TEXTBOX_GAP)
