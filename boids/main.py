"""
Fun with boids.
Small script to play with boids algorythms and create some fun visuals.
"""

import pygame
import random
from .Utils.boids import Horde

# Constants
FPS: int = 30
SIZE: tuple[int, int] = (1280, 720)
EDGES: tuple[int, int, int, int] = (0, SIZE[0], 0, SIZE[1])
ROUND_RADIUS: int = 150
BUTTON_WIDTH, BUTTON_HEIGHT = 240, 100

# Colors
RGB_TITLE: tuple[int, int, int] = (249, 231, 159)
"""Light yellow"""
RGB_BACKGROUND: tuple[int, int, int] = (25, 42, 86)
"""Navy blue"""
RGB_RECTANGLE: tuple[int, int, int, int] = (154, 194, 221, 120)
"""Light pastel blue with transparency"""
RGB_BUTTON1: tuple[tuple[int, int, int]] = ((70, 171, 112), (88, 214, 141))
"""Soft green"""
RGB_BUTTON2: tuple[tuple[int, int, int]] = ((106, 154, 186), (133, 193, 233))
"""Light sky blue"""
RGB_BUTTON3: tuple[tuple[int, int, int]] = ((193, 118, 110), (241, 148, 138))
"""Bright colar"""
RGB_TRANSPARENT = (0, 0, 0, 0)
RGB_TXT_ACTIVE: tuple[int, int, int] = (220, 220, 255)
RGB_TXT_INACTIVE: tuple[int, int, int] = RGB_BACKGROUND

# INFO TEXT CONTENTS
TXT_DEFAULT = \
"""Boids (Bird-oid ojects) is a simulation of flocking behavior in animals like birds or fish.
It demonstrates how simple rules can create complex group dynamics and emergent behavior.
Hover over buttons for more information."""
TXT_BUTTON_1 = \
"""Open a fullscreen window with a live Boids simulation, 
allowing you to add new boids and adjust parameters 
to observe changing flocking behavior in real-time."""
TXT_BUTTON_2 = \
"""Exit to the console for setting parameters to generate a custom animation of the Boids simulation,
which will be saved as a .gif file."""
TXT_BUTTON_3 = \
"""Exit the appliction.
(You can always exit or come back to this menu 
by pressing `ESC` button on the keyboard.)"""

def main():
    # Initialize pygame window
    pygame.init()
    
    screen: pygame.Surface = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("BOIDS")
    clock: pygame.time.Clock = pygame.time.Clock()
    TITLE_FONT: pygame.font = pygame.font.SysFont("Arial Rounded MT Bold", 200) 
    BUTTON_FONT: pygame.font = pygame.font.SysFont("Arial Rounded MT Bold", 50)
    INFO_FONT: pygame.font = pygame.font.SysFont("Arial Rounded MT Bold", 26)

    # Utils - variables
    running: bool = True
    buttons_state: tuple[bool, bool, bool] = [False, False, False]
    # Transparent rectangle
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
    # Title
    title_surface: pygame.Surface = TITLE_FONT.render("Boids", True, RGB_TITLE)
    title_rect: pygame.rect = title_surface.get_rect()
    title_rect = pygame.Rect(SIZE[0] // 2 - title_rect.width // 2, SIZE[1] // 6, 
                            title_rect.width, title_rect.height)
    # Button rectangles
    button1_rect = pygame.Rect((SIZE[0] // 4) - BUTTON_WIDTH // 2, SIZE[1] // 2 - BUTTON_HEIGHT // 2, 
                            BUTTON_WIDTH, BUTTON_HEIGHT)
    button2_rect = pygame.Rect((SIZE[0] // 2) - BUTTON_WIDTH // 2, SIZE[1] // 2 - BUTTON_HEIGHT // 2, 
                            BUTTON_WIDTH, BUTTON_HEIGHT)
    button3_rect = pygame.Rect((3 * SIZE[0] // 4) - BUTTON_WIDTH // 2, SIZE[1] // 2 - BUTTON_HEIGHT // 2, 
                            BUTTON_WIDTH, BUTTON_HEIGHT)
    button1_txt = (BUTTON_FONT.render("Live", True, RGB_TXT_ACTIVE), 
                BUTTON_FONT.render("Live", True, RGB_TXT_INACTIVE))
    button2_txt = (BUTTON_FONT.render("Gif", True, RGB_TXT_ACTIVE), 
                BUTTON_FONT.render("Gif", True, RGB_TXT_INACTIVE))
    button3_txt = (BUTTON_FONT.render("Quit", True, RGB_TXT_ACTIVE), 
                BUTTON_FONT.render("Quit", True, RGB_TXT_INACTIVE))
    button1_txt_rect = button1_txt[0].get_rect(center=button1_rect.center)
    button2_txt_rect = button2_txt[0].get_rect(center=button2_rect.center)
    button3_txt_rect = button3_txt[0].get_rect(center=button3_rect.center)
    # Info rectangle
    info_rect: pygame.rect = pygame.Rect(SIZE[0] // 6, SIZE[1] // 2 + button1_rect.height, 
                                        2 * SIZE[0] // 3, button1_rect.height)
    def render_multiline_text(text: str) -> pygame.Surface:
        """Render multiline text centered within a given rectangle."""
        # Create a temporary surface to render the text
        surface = pygame.Surface(info_rect.size, pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Clear the surface with transparent color

        # Split the text into lines
        lines = text.split('\n')
        line_height = INFO_FONT.get_height() + 5
        total_height = len(lines) * line_height
        
        # Calculate the starting Y position to center the text
        y_offset = (info_rect.height - total_height) // 2

        for line in lines:
            # Render each line of text
            rendered_line = INFO_FONT.render(line, True, RGB_BACKGROUND)
            line_rect = rendered_line.get_rect()
            x_offset = (info_rect.width - line_rect.width) // 2
            surface.blit(rendered_line, (x_offset, y_offset))
            y_offset += line_height 

        return surface
    info_surface_default = render_multiline_text(TXT_DEFAULT)
    info_surface_button1 = render_multiline_text(TXT_BUTTON_1)
    info_surface_button2 = render_multiline_text(TXT_BUTTON_2)
    info_surface_button3 = render_multiline_text(TXT_BUTTON_3)

    # Utils - functions
    def draw_buttons(surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, RGB_BUTTON1[buttons_state[0]], button1_rect, border_radius=20)
        pygame.draw.rect(surface, RGB_BUTTON2[buttons_state[1]], button2_rect, border_radius=20)
        pygame.draw.rect(surface, RGB_BUTTON3[buttons_state[2]], button3_rect, border_radius=20)
        screen.blit(button1_txt[buttons_state[0]], button1_txt_rect)
        screen.blit(button2_txt[buttons_state[1]], button2_txt_rect)
        screen.blit(button3_txt[buttons_state[2]], button3_txt_rect)
    def update_info_window(screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, RGB_RECTANGLE, info_rect, border_radius=100)
        if buttons_state[0]:
            screen.blit(info_surface_button1, info_rect.topleft)
        elif buttons_state[1]:
            screen.blit(info_surface_button2, info_rect.topleft)
        elif buttons_state[2]:
            screen.blit(info_surface_button3, info_rect.topleft)
        else:
            screen.blit(info_surface_default, info_rect.topleft)

    # Initialize Horde of Boids
    horde: Horde = Horde()
    # Initialize Boids
    for _ in range(5):
        coord = (float(random.randint(50, SIZE[0] - 50)), float(random.randint(50, SIZE[1] - 50)))
        for _ in range(30):
            horde.add_boid(coord,
                        (random.randrange(-2, 2), 
                        random.randrange(-2, 2)),
                        60)
            
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
                    # Live simulation
                    if buttons_state[0]:
                        # Quit pygame, run live simulation and close this process
                        pygame.quit()
                        return "display"
                    elif buttons_state[1]:
                        # Quit pygame, run live simulation and close this process   
                        pygame.quit()
                        return "save2gif"
                    elif buttons_state[2]:
                        running = False
            
            # Handle mouse position
            if event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                if button1_rect.collidepoint(x, y):
                    buttons_state = [True, False, False]
                elif button2_rect.collidepoint(x, y):
                    buttons_state = [False, True, False]
                elif button3_rect.collidepoint(x, y):
                    buttons_state = [False, False, True]
                else:
                    buttons_state = [False, False, False]

        # Draw Menu
        screen.fill(RGB_BACKGROUND)
        horde.update(0.0035, 60, 0.06, 90, 0.0005, 0.0045, 15, 5, EDGES, 250)
        horde.draw(screen)
        screen.blit(trans_rect_surface, trans_rect_rect)
        screen.blit(title_surface, title_rect)
        draw_buttons(screen)
        update_info_window(screen)

        # flip frame    
        pygame.display.flip()
        clock.tick(FPS)

    # Quit Pygame and end programm
    pygame.quit()
    return None

