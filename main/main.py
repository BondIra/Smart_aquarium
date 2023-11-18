import pygame


pygame.init()

Icon = pygame.image.load('resources/images/icon.png')
bg = pygame.image.load("resources/images/bg.jpg")
aquarium = pygame.image.load("resources/images/aquarium.png")
aquarium_scale = pygame.transform.scale(aquarium, (900, 550))
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Smart Aquarium')
pygame.display.set_icon(Icon)

running = True

while running:
    clock.tick(60)
    for event in pygame.event.get():
        screen.blit(bg, (0, 0))
        screen.blit(aquarium_scale, (10, 10))
        pygame.display.flip()

        if event.type == pygame.QUIT:
            running = False
