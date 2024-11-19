""""""

# Finnish getting parameters
# Add docstrings

import gc
import os
import pygame
import random
from PIL import Image
from math import log10
from .boids import Horde
from typing import Optional
from loading_bar import LoadingBar


def get_user_settings() -> Optional[dict]:
    """"""

    # Default settings
    settings = {
        "fps": 24, # hash marks it's checked in input function
        "length_in_seconds": 3, #
        "resolution": (1280, 720), #
        "number_of_sources": 5, #
        "boids_per_source": 10, #
        "background_color": "black",
        "boid_color": "dynamic",
        "boid_size": 25,
        "boid_min_speed": 1,
        "boid_max_speed": 5,
        "separation_factor": 0.005,
        "separation_distance": 60,
        "alignment_factor": 0.06,
        "alignment_distance": 90,
        "edge_factor": 0.005,
        "edge_margin": 100,
        "cohesion_factor": 000.5,
    }

    # Function to print settings into console
    def display_settings() -> None:
        os.system("cls")
        print("Welcaome to console boid simulator!")
        print("\nCurrent seettings are:\n")
        for key, value in settings.items():
            print(f"  {key.replace('_', ' ').capitalize()}: {value}")
        print(f"\n  Total number of boids is {settings["boids_per_source"] * settings["number_of_sources"]}")
        print(f"  Total number of frames is {settings["fps"] * settings["length_in_seconds"]}")
        print("\n")

    # Input interface
    def input_settings() -> None:
        os.system("cls")
        print("Press Enter to keep the default value for each setting.\n")

        for key, value in settings.items():
            # fps | length_in_seconds | number_of_sources
            if key == "fps" or \
               key == "length_in_seconds" or \
               key == "number_of_sources" or \
               key == "boids_per_source":
                input_value = input(f"{key.replace('_', ' ').capitalize()} (default: {value}): ")
                if input_value.strip():  # Only update if the user provides input
                    try:
                        i_value = int(input_value)                        
                        if i_value >= 1: 
                            settings[key] = i_value
                        else: 
                            print(f"Invalid input. Number of {key.replace('_', ' ').capitalize()} key must be at least equal to 1, Using default value: {value}")
                    except ValueError:
                        print(f"Invalid input. Using default value: {value} for {key.replace('_', ' ').capitalize()}")   
            
            # resolution
            if key == "resolution":
                input_value_w = input(f"{key.replace('_', ' ').capitalize()}-width  (default: {value[0]}): ")
                input_value_h = input(f"{key.replace('_', ' ').capitalize()}-height (default: {value[1]}): ")
                new_w, new_h = value
                
                if input_value_w.strip():
                    try:
                        width = int(input_value_w)
                        if width >= 100:
                            new_w = width
                        else:
                            print(f"Invalid input. {key.replace('_', ' ').capitalize()}-width key must be at least equal to 100, Using default value: {value}")
                    except ValueError:
                        print(f"Invalid input. Using default value: {value} for {key.replace('_', ' ').capitalize()}-width")
                
                if input_value_h.strip():
                    try:
                        height = int(input_value_h)
                        if height >= 100:
                            new_h = height
                        else:
                            print(f"Invalid input. {key.replace('_', ' ').capitalize()}-height key must be at least equal to 100, Using default value: {value}")
                    except ValueError:
                        print(f"Invalid input. Using default value: {value} for {key.replace('_', ' ').capitalize()}-height")

                settings[key] = new_w, new_h
                

                """try:
                    # Convert numbers and tuples automatically
                    if isinstance(value, int):
                        settings[key] = int(input_value)
                    elif isinstance(value, float):
                        settings[key] = float(input_value)
                    elif isinstance(value, tuple) or "color" in key.lower():
                        settings[key] = str(input_value).lower()  # Keep as string
                    else:
                        settings[key] = input_value
                except ValueError:
                    #print(f"Invalid input for {key}, using default value: {value}")
                    pass"""

    # Display help statement
    def display_help() -> bool:
        while(True):
            os.system("cls")
            print("Boids generator will render gif animation of boids for gien parameters.\n" +
                f"Animation will be saved in Animations folder in the current directory: {os.getcwd()}\Animations),\n" +
                "under the name: (number of boids)_boids_(animation_length)s_animation.gif.\n" +
                "\nParameters:\n\n`Number of sources`, `Boids Per Source`:\n" +
                "At the start of the animation boids will be generated in randomly placed sources,\n" +
                "with random velocities (in the given range).\n" +
                "\n`Boid Size`, `Boid [...] Speed`, `[...] Distance`, `Edge Margin`:\n" +
                "All of those values are in pixels.")
            
            ans: str = input("\n\nGo back to setting animation [P]arameters or to [M]ain menu: ")
            if ans == 'p' or ans == 'P': return False
            elif ans == 'm' or ans == 'M': return True

    # Asking user whether he wants to change settings till hi is satisfied
    while(True): 
        display_settings()
        ans: str = input("Would you like to [C]hange parameters or [G]enerate animation? ([H]elp, [E]xit):")
        if ans == 'g' or ans == 'G': break
        elif ans == 'c' or ans == 'C': input_settings()
        elif ans == 'h' or ans == 'H': 
            if display_help(): 
                return None
        elif ans == 'e' or ans == 'E': return None

    return settings

def save2gif() -> None:
    """"""

    # Get parameters
    settings: dict = get_user_settings()
    if settings == None: return

    # Set parameters
    frames: list[Image.Image] = []
    FRAME_DURATION: float = 1/settings["fps"]
    ANIMATION_DURATION: int = settings["length_in_seconds"] * settings["fps"]
    RES: tuple[int, int] = settings["resolution"]
    screen: pygame.Surface = pygame.Surface(RES)
    EDGES: tuple[int, int, int, int] = (0, RES[0], 0, RES[1])
    SEP_F, SEP_D, ALI_F, ALI_D, COH_F, EDGE_F,MAX_S, MIN_S = \
        settings["separation_factor"], settings["separation_distance"], \
        settings["alignment_factor"], settings["alignment_distance"], \
        settings["cohesion_factor"], settings["edge_factor"], \
        settings["boid_max_speed"], settings["boid_min_speed"]

    # Create boids
    horde: Horde = Horde()
    # Populate horde
    MARGIN: int = settings["edge_margin"]
    x_range: tuple[int, int] = (MARGIN, RES[0] - MARGIN)
    y_range: tuple[int, int] = (MARGIN, RES[1] - MARGIN)
    size = settings["boid_size"]
    for _ in range(settings["number_of_sources"]):
        coord = (float(random.randint(*x_range)), float(random.randint(*y_range)))
        for _ in range(settings["boids_per_source"]):
            horde.add_boid(coord, (random.randrange(-MAX_S, MAX_S), random.randrange(-MAX_S, MAX_S)), size)
            
    os.system("cls")
    print("Rendering process started\n")
    print("Number of frames to render:", ANIMATION_DURATION) 
    print("Number of boids to render: ", len(horde.positions))
    print(f"Frame resolution:           {RES[0]}x{RES[1]}\n")

    # Rendering loop
    bar: LoadingBar = LoadingBar(total=ANIMATION_DURATION)
    skip: int = int(10**(log10(ANIMATION_DURATION)//1 - 2))
    for frame_num in range(1, ANIMATION_DURATION + 1):
        # Update loading bar
        bar.update(frame_num, skip_every_other=skip)

        # Draw frame:
        # Draw background
        screen.fill(settings["background_color"])
        # Update boids
        horde.update(SEP_F, SEP_D, ALI_F, ALI_D, COH_F, EDGE_F, MAX_S, MIN_S, EDGES, MARGIN)
        # Draw boids
        horde.draw(screen)

        # Process image
        frame_image = pygame.image.tostring(screen, 'RGB')
        frame_image = Image.frombytes('RGB', screen.get_size(), frame_image)
        frames.append(frame_image.quantize(colors=256))

    # Close loading bar
    bar.close(display_statement=True)

    print("GIF succesfully rendered.")
    print("\nSaving gif, it can take up to a few minutes...", end='\r')

    # Name image
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    name = os.path.join(parent_dir, "Animations", 
                        f"{len(horde.positions)}_boids_{settings["length_in_seconds"]}s_animation.gif")
    # Numarate image
    counter = 1
    while os.path.exists(name):
        name = os.path.join(parent_dir, "Animations",
                f"{len(horde.positions)}_boids_{settings["length_in_seconds"]}s_animation({counter}).gif")
        counter += 1
    
    # Save image
    gc.collect()
    frames[0].save(name, 
                   save_all=True, 
                   append_images=frames[1:], 
                   duration=FRAME_DURATION, 
                   optimize=True,
                   loop=0)
    
    print("Finnished. GIF file is saved under:", name)
    input("\nPress Enter to come back to main menu...")

    # Quit Pygame and come back to main script
    pygame.quit()

