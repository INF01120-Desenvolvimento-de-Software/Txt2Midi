import pygame
import screenManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Txt2Midi")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)

    manager = screenManager.screenManager(font)

    manager.change_state("start")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.handle_event(event)

        manager.update()
        manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
