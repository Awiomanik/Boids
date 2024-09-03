"""
Fun with boids.
Small script to play with boids algorythms and create some fun visuals.
"""
import pygame
import sys
import random 
from boids import Boid, Horde
from input_boxes import InputBox

# Initialize pygame window
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = SIZE = screen.get_size()
clock = pygame.time.Clock()

# Constants
BLACK: tuple[int, int, int] = (30, 30, 30)
DOTS: tuple[int, int, int] = (150, 10, 10)
SETTINGS_ICON: pygame.Surface = pygame.image.load("settings_icon.png").convert_alpha()
CLOSE_ICON: pygame.Surface = pygame.image.load("close_icon.png").convert_alpha()
SETTINGS_ICON_RECT: pygame.Rect = pygame.Rect(1810, 60, 50, 50)

# Utils
running: bool = True
settings: bool = False

# Boids
horde: Horde = Horde()

# Parameters
parameters: list[InputBox] = [
    InputBox(0., 1400, 150, name="test_value"),
    InputBox(0.05, 1400, 250, name="separation_factor")
]

# Mask
def create_mask(dot_radius: int = 15, spacing: int = 40):
    mask = pygame.Surface(SIZE)
    mask.fill(BLACK)
    
    # Draw red dots around the edges
    for x in range(spacing, WIDTH - spacing, spacing):
        pygame.draw.circle(mask, DOTS, (x, spacing), dot_radius)  # Top edge
        pygame.draw.circle(mask, DOTS, (x, HEIGHT-spacing + 1), dot_radius)  # Bottom edge
    
    for y in range(spacing, HEIGHT - spacing + 1, spacing):
        pygame.draw.circle(mask, DOTS, (spacing, y), dot_radius)  # Left edge
        pygame.draw.circle(mask, DOTS, (WIDTH-spacing, y), dot_radius)  # Right edge

    return mask

mask = create_mask()

# Main loop
while running:
    # Handle input
    for event in pygame.event.get():
        # Handle closing the window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        # Handle input boxes
        if settings:
            for box in parameters:
                box.handle_event(event)

        # Handle mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Left click
            if event.button == 1:  
                x, y = pygame.mouse.get_pos()

                # Trigger settings
                if SETTINGS_ICON_RECT.collidepoint(x, y):
                    settings = not settings
                
                # Add boid
                else:
                    horde.add_boid((float(x), float(y)), 
                                   (random.randrange(-2, 2), random.randrange(-2, 2)))

            # Right click
            elif event.button == 3:  
                # Add barrier
                pass

    # Draw background
    screen.blit(mask, (0, 0))

    # Update boids
    horde.update(0.05, 20, 0.005, 40, 0.0005)
    
    # Draw boids
    horde.draw(screen)

    # Draw parameters
    if settings:
        # draw icon
        screen.blit(CLOSE_ICON, SETTINGS_ICON_RECT)
        # draw boxes
        for box in parameters:
            box.draw(screen)
    else:
        screen.blit(SETTINGS_ICON, SETTINGS_ICON_RECT)

    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()


