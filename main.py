"""
Fun with boids.
Small script to play with boids algorythms and create some fun visuals.
"""
import pygame
import sys

# Colors
RGB_BACKGROUND: tuple[int, int, int] = (25, 42, 86)
"""Navy blue"""
RGB_RECTANGLE: tuple[int, int, int, int] = (174, 214, 241, 40)
"""Light pastel blue with transparency"""
RGB_BUTTON1: tuple[int, int, int] = (241, 148, 138)
"""Bright colar"""
RGB_TRANSPARENT = (0, 0, 0, 0)

# Constants
FPS: int = 30
SIZE: tuple[int, int] = (1280, 720)
ROUND_RADIUS: int = 150

# Initialize pygame window
pygame.init()
screen: pygame.Surface = pygame.display.set_mode(SIZE)
pygame.display.set_caption("BOIDS")
clock: pygame.time.Clock = pygame.time.Clock()

# Utils
running: bool = True
trans_rect_rect: pygame.Rect = pygame.Rect(SIZE[0] // 10 - ROUND_RADIUS, 
                                           SIZE[1] // 10 - ROUND_RADIUS, 
                                           (SIZE[0] // 10) * 8 + 2 * ROUND_RADIUS, 
                                           (SIZE[1] // 10) * 8 + 2 * ROUND_RADIUS)
trans_rect_surface: pygame.Surface = pygame.Surface(trans_rect_rect.size, pygame.SRCALPHA)
trans_rect_surface.fill(RGB_TRANSPARENT)
pygame.draw.rect(trans_rect_surface, RGB_RECTANGLE, (ROUND_RADIUS, ROUND_RADIUS, 
                                                     trans_rect_rect.width - 2 * ROUND_RADIUS, 
                                                     trans_rect_rect.height - 2 * ROUND_RADIUS), 
                 border_radius=ROUND_RADIUS)

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

        # Handle mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Left click
            if event.button == 1:  
                x, y = pygame.mouse.get_pos()
                pass
            # Right click
            elif event.button == 3: 
                pass

    # Draw Menu
    screen.fill(RGB_BACKGROUND)
    screen.blit(trans_rect_surface, trans_rect_rect)

    # flip frame    
    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()

