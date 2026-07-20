# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for details.

from icecream import ic
import pygame
import pygame.gfxdraw


def main():
    pygame.init()
    window = pygame.Window(
        size=(530, 530), title="Grafic Primitives ", position=(10, 50)
    )
    screen = window.get_surface()
    clock = pygame.time.Clock()

    ic()
    mygrey = pygame.Color(200, 200, 200)
    myrectangle1 = pygame.Rect(10, 10, 20, 30)
    myrectangle2 = pygame.Rect(60, 10, 20, 30)
    points1 = ((120, 10), (160, 10), (140, 90))
    points2 = ((180, 10), (220, 10), (200, 90))

    # Custom color
    # Rectangle object
    # List of points

    ic()
    running = True
    while running:
        ic()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        ic()
        screen.fill(mygrey)
        pygame.draw.rect(screen, "red", myrectangle1)  # Filled rectangle
        pygame.draw.rect(screen, "red", myrectangle2, 3, 5)  # Rectangle outline
        pygame.draw.polygon(screen, "green", points1)  # Filled polygon
        pygame.draw.polygon(screen, "green", points2, 1)  # Polygon outline
        pygame.draw.line(screen, "red", (5, 230), (240, 230), 3)  # Line
        pygame.draw.circle(screen, "blue", (40, 150), 30)  # Filled circle
        pygame.draw.circle(screen, "blue", (110, 150), 30, 2)  # Circle outline
        pygame.draw.circle(screen, "blue", (180, 150), 30, 5, True)  # Arc segment

        for i in range(255):
            for j in range(255):
                screen.set_at((265 + i, 10 + j), (255, i, j))
                screen.fill((i, j, 255), ((10 + i, 265 + j), (1, 1)))
                pygame.gfxdraw.pixel(screen, 265 + i, 265 + j, (i, 255, j))
        window.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
