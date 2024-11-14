import pygame
import random 
import gc
import os
from PIL import Image
from loading_bar import LoadingBar
from .boids import Horde

def save2gif() -> None:
    """"""
    frames = []
    FRAME_DURATION = 35
    animation_duration = 2
    animation_duration *= 33

    # Initialize pygame window
    screen = pygame.Surface((1280, 720))
    WIDTH, HEIGHT = SIZE = screen.get_size()
    clock = pygame.time.Clock()

    # Utils
    running: bool = True
    settings: bool = False

    # Boids
    horde: Horde = Horde()
    # Populate horde
    for i in range(5):
        coord = (float(random.randint(100, 1180)), float(random.randint(100, 620)))
        for _ in range(200):
            horde.add_boid(coord,
                        (random.randrange(-2, 2), 
                        random.randrange(-2, 2)))
    print("Number of boids to render:", len(horde.positions))

    # Rendering loop
    bar: LoadingBar = LoadingBar(total=animation_duration, additional_info="Hey!!")
    for frame_num in range(1, animation_duration + 1):
        # Update loading bar
        bar.update(frame_num)

        # Draw frame:
        # Draw background
        screen.fill((0, 0, 0))
        # Update boids
        horde.update(0.02, 20, 0.05, 100, 0.002, 0.01, 15, 1, (0, 1280, 0, 720))
        # Draw boids
        horde.draw(screen)

        # Process image
        frame_image = pygame.image.tostring(screen, 'RGB')
        frame_image = Image.frombytes('RGB', screen.get_size(), frame_image)
        frames.append(frame_image)

    bar.close(display_statement=True, additional_info="gif successfully rendered")

    # Save image to gif
    if frames:
        # Name image
        print("\nCreating gif...", end='\r')
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        name = os.path.join(parent_dir, f"Animations//{len(horde.positions)}_boids_animation.gif")
        # Numarate image
        counter = 1
        while os.path.exists(name):
            name = os.path.join(parent_dir, 
                    f"Animations//{len(horde.positions)}_boids_animation({counter}).gif")
            counter += 1
        
        # Save image
        gc.collect()
        frames[0].save(name, save_all=True, append_images=frames[1:], duration=FRAME_DURATION, loop=0)
        print("Finnished. GIF file is saved under:", name)

    # Quit Pygame and come back to main script
    pygame.quit()

