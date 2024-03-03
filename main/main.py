import pygame
import sys
from datetime import datetime

pygame.init()

Icon = pygame.image.load('resources/images/icon.png')
bg = pygame.image.load("resources/images/bg.jpg")
aquarium = pygame.image.load("resources/images/aquarium.png")
font_1 = "resources/fonts/font1.ttf"
button_sound = pygame.mixer.Sound("resources/sounds/button_sound.mp3")
pygame.display.set_caption('Smart Aquarium')
pygame.display.set_icon(Icon)
pygame.mixer.music.load("resources/sounds/music.mp3")
button_on_image = pygame.image.load("resources/images/SoundOn.png")
button_off_image = pygame.image.load("resources/images/SoundOff.png")

button_on_image = pygame.transform.scale(button_on_image, (50, 50))
button_off_image = pygame.transform.scale(button_off_image, (50, 50))
screen = pygame.display.set_mode((1280, 720))
aquarium_scale = pygame.transform.scale(aquarium, (900, 550))

class Label:
    def __init__(self, font_size, position, color=(225, 255, 255)):
        self.color = color
        self.surface = None
        self.font = pygame.font.Font("resources/fonts/font1.ttf", font_size)  # Font
        self.color = (64, 64, 64)  # Text colour
        self.rect = pygame.Rect(position, (0, 0))

    def update_text(self, text):
        self.surface = self.font.render(text, True, self.color)
        self.rect.width, self.rect.height = self.surface.get_size()

    def draw(self, screen1):
        screen1.blit(self.surface, self.rect)

def print_text(message, x, y, font_color=(0, 0, 0), font_type=font_1, font_size=30):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))

def test():
    print("lo o lo lo loo")
    screen.blit(aquarium_scale, (100, 100))
    pass

# Function to toggle music and button image
def toggle_music():
    global button_state
    if button_state:
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    else:
        pygame.mixer.music.stop()

    button_state = not button_state

# New location for the button
button_location = (1100, 20)
# Initialize button state
button_state = True  # True for music on, False for music off

# Create a label
timing = Label(16, (1100, 20))
# Main game loop
clock = pygame.time.Clock()

screen.blit(bg, (0, 0))
screen.blit(aquarium_scale, (10, 10))

print_text('message', 900, 100, font_color=(0, 0, 0), font_type=font_1, font_size=30)

# Run the game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if the mouse click is within the button area
            button_rect = button_on_image.get_rect(topleft=button_location)
            if button_rect.collidepoint(event.pos):
                toggle_music()

    # Draw the button based on the current state
    if button_state:
        screen.blit(button_on_image, button_location)
    else:
        screen.blit(button_off_image, button_location)

    pygame.display.flip()
    clock.tick(60)  # Cap the frame rate to 60 FPS

    # Get the current date and time
    now = datetime.now()
    current_day = now.strftime("%a").strip()
    current_date = now.strftime("%b %d").strip()
    current_time = now.strftime("%H:%M:%S").strip()

    # Update and draw the label with the current date and time
    label_text = f"{current_day} {current_date}  {current_time}"
    timing.update_text(label_text)

    # Draw only the area where the label is located
    screen.fill((224, 224, 224), timing.rect)
    timing.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(1)  # Update every 1 sec


