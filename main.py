import pygame
from ui.ScreenManager import ScreenManager
from ui import Layout, Theme


def main():
    pygame.init()
    pygame.key.set_repeat(Layout.KEY_REPEAT_DELAY_MS, Layout.KEY_REPEAT_INTERVAL_MS)
    screen = pygame.display.set_mode((Layout.WINDOW_WIDTH, Layout.WINDOW_HEIGHT))
    pygame.display.set_caption("Txt2Midi")
    clock = pygame.time.Clock()

    manager = ScreenManager()

    manager.change_state("start")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.handle_event(event)

        manager.draw(screen)

        pygame.display.flip()
        clock.tick(Layout.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()