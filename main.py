import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("AI Robot Commander")

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((240, 240, 240))
    pygame.display.flip()

pygame.quit()