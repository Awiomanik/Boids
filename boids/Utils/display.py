import pygame
import random 
from .boids import Horde
from boids.Utils.input_boxes import InputBox

def display() -> None:
    """
    Displays a full-screen interactive simulation of boids with customizable parameters.

    The `display` function initializes a Pygame window, manages user interactions, and renders
    boids in real time. Users can interact with the simulation by adjusting parameters using input boxes,
    toggling settings mode, and adding new boids with mouse clicks.

    Features:
    - Full-screen rendering with an overlay mask for aesthetics.
    - Adjustable boid simulation parameters, such as separation, alignment, cohesion, and speed.
    - Interactive interface with toggleable settings and the ability to add boids dynamically.

    Usage:
        Call `display()` to start the simulation. Use the following interactions:
        - Left-click on the simulation area to add boids.
        - Click the settings icon to toggle the parameter adjustment interface.
        - Right-click (future functionality) to add barriers or predators.
        - Press `ESC` or close the window to exit the simulation.

    Dependencies:
        - Pygame: For rendering and interaction.
        - boids.Horde: Manages the boid simulation logic.
        - boids.Utils.input_boxes.InputBox: Handles adjustable input parameters.

    Notes:
        - Requires the following resources:
          - `boids/Utils/GFX/settings_icon.png`: Icon for opening the settings menu.
          - `boids/Utils/GFX/close_icon.png`: Icon for closing the settings menu.

    Example:
        from boids.Utils.display import display
        display()
    """
    # Initialize pygame window
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = SIZE = screen.get_size()
    clock = pygame.time.Clock()

    # Constants
    BLACK: tuple[int, int, int] = (30, 30, 30)
    DOTS: tuple[int, int, int] = (150, 10, 10)
    SETTINGS_ICON: pygame.Surface = pygame.image.load("boids/Utils/GFX/settings_icon.png").convert_alpha()
    CLOSE_ICON: pygame.Surface = pygame.image.load("boids/Utils/GFX/close_icon.png").convert_alpha()
    SETTINGS_ICON_RECT: pygame.Rect = pygame.Rect(1810, 60, 50, 50)
    FPS = 30

    # Utils
    running: bool = True
    settings: bool = False

    # Boids
    horde: Horde = Horde()

    # Parameters
    parameters: list[InputBox] = [
        InputBox(0.02, 1450, 120, name="separation_factor"),
        InputBox(20, 1450, 220, name="separation_distance"),
        InputBox(0.05, 1450, 320, name="alignment_factor"),
        InputBox(100, 1450, 420, name="alignment_distance"),
        InputBox(0.002, 1450, 520, name="cohesion_factor"),
        InputBox(0.01, 1450, 620, name="edge_factor"),
        InputBox(10, 1450, 720, name="top_speed"),
        InputBox(1, 1450, 820, name="bottom_speed")
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
                    elif (settings and x < 1450) or not settings:
                        top_speed = int(parameters[6].val)
                        for _ in range(random.randint(1, 20)):
                            horde.add_boid((float(x), float(y)), 
                                        (random.randrange(-top_speed, top_speed), 
                                        random.randrange(-top_speed, top_speed)))

                # Right click
                elif event.button == 3:  
                    # Add barrier or predator
                    pass

        # Draw background
        screen.blit(mask, (0, 0))

        # Update boids
        horde.update(parameters[0].val, 
                    parameters[1].val, 
                    parameters[2].val, 
                    parameters[3].val, 
                    parameters[4].val,
                    parameters[5].val,
                    parameters[6].val,
                    parameters[7].val)
        
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
        clock.tick(FPS)

    # Quit Pygame, go back to main script
    pygame.quit()



