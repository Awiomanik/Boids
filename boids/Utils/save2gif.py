"""
Boids GIF Renderer

This script provides functionality for configuring, simulating, and rendering animations of boids
(a simulation of flocking birds or similar agents). The script includes tools for:

1. Allowing users to customize simulation parameters through a console-based interface.
2. Rendering and saving the simulation as an optimized GIF based on user-defined parameters.

Key Features:
- Support for multiple species of boids with independent parameters.
- Configurable resolution, frame rate, boid behavior, and aesthetic options.
- Real-time rendering progress visualization via a loading bar.

Dependencies:
- pygame: For rendering and simulation.
- Pillow: For creating and saving the GIF.
- numpy: For boid computations.
- loading_bar: A custom utility for progress visualization.
"""

import gc
import os
import copy
import pygame
import random
from PIL import Image
from math import log10
from .boids import Horde
from typing import Optional
from loading_bar import LoadingBar


def get_user_settings() -> Optional[tuple[dict, list[dict]]]:
    """
    Configure simulation parameters through a console-based interface.

    This function allows users to customize parameters for the boids simulation, including general
    settings (e.g., resolution, frame rate, background color) and species-specific settings (e.g., 
    boid behavior and aesthetics). Defaults are displayed, and users can modify settings interactively.

    Returns:
        Optional[tuple[dict, list[dict]]]: 
        - A tuple containing:
            1. A dictionary of general settings.
            2. A list of dictionaries, each representing the parameters for one species of boids.
        - Returns None if the user chooses to exit the configuration process.

    Example:
        settings, species = get_user_settings()
        if settings is not None:
            print("Simulation configured successfully.")
    """

    # Default settings
    settings_default: dict = {
        "fps": 24, # done
        "length_in_seconds": 3, # done
        "resolution": (1280, 720), # done
        "background_color": "black", # done
        "number_of_species": 1 # done
    }
    specie_default: dict = {
            "number_of_sources": 5, 
            "boids_per_source": 10, 
            "boid_size": 25, 
            "boid_min_speed": 1, 
            "boid_max_speed": 5, 
            "separation_factor": 0.005, 
            "separation_distance": 60, 
            "alignment_factor": 0.06, 
            "alignment_distance": 90, 
            "cohesion_factor": 0.005, 
            "edge_factor": 0.005, 
            "edge_margin": 100,
            "boid_color": "green-purple"
    }

    settings: dict = copy.deepcopy(settings_default)
    species: list[dict] = [copy.deepcopy(specie_default)]

    # Function to print settings into console
    def display_settings() -> None:
        os.system("cls")
        print("Welcaome to console boid simulator!")

        print("\nGeneral parameters are set to:\n")
        for key, value in settings.items():
            print(f"  {key.replace('_', ' ').capitalize()}: {value}")
        print(f"\n  Total number of frames is {settings["fps"] * settings["length_in_seconds"]}.")

        boids_total: int = 0
        for i, specie in enumerate(species):
            print(f"\nParameters of specie {i + 1} (of {settings["number_of_species"]}):\n")
            for key, value in specie.items():
                print(f"  {key.replace('_', ' ').capitalize()}: {value}")
            specie_total = specie["boids_per_source"] * specie["number_of_sources"]
            boids_total += specie_total
            print(f"\n  Total number of boids in a specie is {specie_total}.")
        print(f"\n  Total number of boids is {boids_total}.")
        print("\n")

    # Input interface
    def input_settings() -> None:
        os.system("cls")
        print("Press Enter to keep the default value for each setting.\n")

        # Set geeral parameters
        for key, value in settings_default.items():
            default = settings_default[key]
            # fps | length_in_seconds | number_of_species
            if key in ["fps", "length_in_seconds", "number_of_species"]:
                input_value = input(f"{key.replace('_', ' ').capitalize()} (default: {default}): ")
                if input_value.strip():
                    try:
                        i_value = int(input_value)                        
                        if i_value >= 1: 
                            settings[key] = i_value
                        else: 
                            print(f"Invalid input. Number of {key.replace('_', ' ').capitalize()} " + \
                                  f"key must be at least equal to 1, " + \
                                  f"Using default value: {default}")
                            settings[key] = default
                    except ValueError:
                        print(f"Invalid input. Using default value " + \
                              f"{default} for {key.replace('_', ' ').capitalize()}")  
                        settings[key] = default
            # resolution
            elif key == "resolution":
                input_value_w = input(f"{key.replace('_', ' ').capitalize()}-width  (default: {default[0]}): ")
                input_value_h = input(f"{key.replace('_', ' ').capitalize()}-height (default: {default[1]}): ")
                new_w, new_h = settings[key]
                
                if input_value_w.strip():
                    try:
                        width = int(input_value_w)
                        if width >= 100:
                            new_w = width
                        else:
                            print(f"Invalid input. {key.replace('_', ' ').capitalize()}-width" + \
                                  f" key must be at least equal to 100, Using default value: {default}")
                            new_w = default[0]
                    except ValueError:
                        print(f"Invalid input. Using default value {default}" + \
                              f" for {key.replace('_', ' ').capitalize()}-width")
                        new_w = default[0]
                
                if input_value_h.strip():
                    try:
                        height = int(input_value_h)
                        if height >= 100:
                            new_h = height
                        else:
                            print(f"Invalid input. {key.replace('_', ' ').capitalize()}-height " + \
                                  f"key must be at least equal to 100, Using default value: {default}")
                            new_w = default[0]
                    except ValueError:
                        print(f"Invalid input. Using default value: {value}" + \
                              f" for {key.replace('_', ' ').capitalize()}-height")
                        new_w = default[0]
                        
                settings[key] = new_w, new_h
            # background color 
            elif key == "background_color":
                input_value = input(f"{key.replace('_', ' ').capitalize()}" + \
                                    f" (input RGB to set precise rgb values) (default: {default}): ")
                if input_value.strip():
                    input_value = input_value.lower()
                    if input_value == "rgb":
                        rgb: tuple[int, int, int] = [0, 0, 0]
                        try:
                            rgb[0] = int(input("Input value for red (0-255): ").strip())
                            rgb[1] = int(input("Input value for green (0-255): ").strip())
                            rgb[2] = int(input("Input value for blue (0-255): ").strip())
                        except:
                            print("Invalid RGB values. Using default: 'black' (0, 0, 0)")
                            rgb = default
                        for i, val in enumerate(rgb): 
                            if not (0 <= val and val <= 255):
                                print(f"RGB values must be in range 0 to 255, {val}" + \
                                      " is out of scope. Using default value: 0")
                                rgb[i] = 0
                        settings["background_color"] = rgb

                    else:
                        try:
                            pygame.Color(input_value)
                            settings["background_color"] = input_value
                        except ValueError:
                            print(f"Invalid input. Using default value {default}" + \
                                  f" for {key.replace('_', ' ').capitalize()}")
                            settings["background_color"] = default

        # Initialize species
        nonlocal species 
        species = [copy.deepcopy(specie_default)]
        for _ in range(settings["number_of_species"] - 1): species.append(copy.deepcopy(specie_default))

        # Set specie specific parameters
        for i, specie in enumerate(species):
            print(f"\n{i + 1}/{settings["number_of_species"]} specie:")

            for key, value in specie.items():
                default = species[i][key]
                # number_of_sources | boids_per_source | boid_size
                if key in ["number_of_sources", "boids_per_source", "boid_size", "boid_min_speed", 
                        "boid_max_speed", "edge_margin", "alignment_distance", "separation_distance"]:
                    
                    ten: bool = key in ["boid_size", "edge_margin", "alignment_distance", "separation_distance"]
                    input_value = input(f"{key.replace('_', ' ').capitalize()} (default: {default}): ")
                    if input_value.strip():
                        try:
                            i_value = int(input_value)                        
                            if i_value >= (10 if ten else 1): 
                                species[i][key] = i_value
                            else: 
                                print(f"Invalid input. Number of {key.replace('_', ' ').capitalize()} " + \
                                    f"key must be at least equal to {10 if ten else 1}, " + \
                                    f"Using default value: {default}")
                                species[i][key] = default
                        except ValueError:
                            print(f"Invalid input. Using default value " + \
                                f"{default} for {key.replace('_', ' ').capitalize()}")  
                            species[i][key] = default
                
                # factors
                elif "factor" in key:
                    input_value = input(f"{key.replace('_', ' ').capitalize()} (default: {default}): ")
                    if input_value.strip():
                        try:
                            i_value = float(input_value)                        
                            if i_value < 1: 
                                species[i][key] = i_value
                            else: 
                                print(f"Invalid input. Number of {key.replace('_', ' ').capitalize()} " + \
                                    f"key must be at most equal to {1}, " + \
                                    f"Using default value: {default}")
                                species[i][key] = default
                        except ValueError:
                            print(f"Invalid input. Using default value " + \
                                f"{default} for {key.replace('_', ' ').capitalize()}")  
                            species[i][key] = default
                    
                # boid_color
                elif key == "boid_color":
                    input_value = input(f"{key.replace('_', ' ').capitalize()} (default: {default}): ")
                    if input_value in ["green-purple", "purple-green", "black&white"]:
                        species[i][key] = input_value

                    elif input_value.startswith("const"):
                        try:
                            rgb: tuple[int, int, int] = [int(x) for x in input_value.split()[1:]]
                        except:
                            print("Invalid RGB values. Using default: 'black' (0, 0, 0)")
                            rgb = default
                        for j, val in enumerate(rgb): 
                            if not (0 <= val and val <= 255):
                                print(f"RGB values must be in range 0 to 255, {val}" + \
                                      " is out of scope. Using default value: 0")
                                rgb[j] = 0

                        species[i][key] = "const " + str(rgb[0]) + ' ' + str(rgb[1]) + ' ' + str(rgb[2])

    # Display help statement
    def display_help() -> bool:
        while(True):
            os.system("cls")
            print("Boids generator will render gif animation of boids for gien parameters.\n" +
                f"Animation will be saved in Animations folder in the current directory: {os.getcwd()}\Animations,\n" +
                "under the name: (number of boids)_boids_(animation_length)s_animation.gif.\n" +
                "\nParameters:\n\n`Number of sources`, `Boids Per Source`:\n" +
                "At the start of the animation boids will be generated in randomly placed sources,\n" +
                "with random velocities (in the given range).\n" +
                "\n`Boid Size`, `Boid [...] Speed`, `[...] Distance`, `Edge Margin`:\n" +
                "All of those values are in pixels.\n" + \
                "\n`boids_color`:\n" + \
                "Custom string parameter that can take following values:\n" + \
                "`green-purple` (default), `purple-green`, `black&white`, or a constant RGB value specified as `const R G B`." )
            
            ans: str = input("\n\nGo back to setting animation [P]arameters or to [M]ain menu: ")
            if ans == 'p' or ans == 'P': return False
            elif ans == 'm' or ans == 'M': return True

    # Asking user whether he wants to change settings till hi is satisfied
    while(True): 
        display_settings()
        ans: str = input("Would you like to [C]hange parameters,\n" + \
                         "set them back to [D]efault \n" + \
                         "or [G]enerate animation?\n" + \
                         "([H]elp, [E]xit):")
        if ans == 'g' or ans == 'G': 
            break
        elif ans == 'c' or ans == 'C': 
            input_settings()
        elif ans == 'd' or ans == 'D': 
            settings = copy.deepcopy(settings_default)
            species = [copy.deepcopy(specie_default)]
        elif ans == 'h' or ans == 'H': 
            if display_help(): 
                return None
        elif ans == 'e' or ans == 'E': 
            return None

    return settings, species

def save2gif() -> None:
    """
    Render and save the boids simulation as an optimized GIF.

    This function handles:
    1. Retrieving simulation parameters via `get_user_settings`.
    2. Generating frames of the simulation based on user-defined settings.
    3. Optimizing and saving the rendered frames as a GIF.

    Features:
    - Supports multiple species with independent parameters.
    - Displays a progress bar during rendering.
    - Automatically names and enumerates GIF files to avoid overwriting.

    Example:
        save2gif()
        # Outputs a GIF to the `Animations` directory based on simulation parameters.
    """

    # Get parameters
    settings: tuple[dict, list[dict]] = get_user_settings()
    if settings == None: return
    settings, species = settings

    # Set parameters
    frames: list[Image.Image] = []
    FRAME_DURATION: float = 1/settings["fps"]
    ANIMATION_DURATION: int = settings["length_in_seconds"] * settings["fps"]
    RES: tuple[int, int] = settings["resolution"]
    screen: pygame.Surface = pygame.Surface(RES)
    EDGES: tuple[int, int, int, int] = (0, RES[0], 0, RES[1])

    # Create boids
    horde: list[Horde] = []
    boids_total: int = 0
    for specie in species:
        subhorde: Horde = Horde(specie["boid_color"])
        # Populate horde
        MARGIN: int = specie["edge_margin"]    
        SEP_F, SEP_D, ALI_F, ALI_D, COH_F, EDGE_F,MAX_S, MIN_S = \
            specie["separation_factor"], specie["separation_distance"], \
            specie["alignment_factor"], specie["alignment_distance"], \
            specie["cohesion_factor"], specie["edge_factor"], \
            specie["boid_max_speed"], specie["boid_min_speed"]
        x_range: tuple[int, int] = (MARGIN, RES[0] - MARGIN)
        y_range: tuple[int, int] = (MARGIN, RES[1] - MARGIN)
        size = specie["boid_size"]
        for _ in range(specie["number_of_sources"]):
            coord = (float(random.randint(*x_range)), float(random.randint(*y_range)))
            for _ in range(specie["boids_per_source"]):
                subhorde.add_boid(coord, (random.randrange(-MAX_S, MAX_S), 
                                          random.randrange(-MAX_S, MAX_S)), size)
        horde.append((subhorde, (SEP_F, SEP_D, ALI_F, ALI_D, COH_F, EDGE_F,MAX_S, MIN_S, EDGES, MARGIN)))
        boids_total += len(subhorde.positions)

    os.system("cls")
    print("Rendering process started\n")
    print("Number of frames to render:", ANIMATION_DURATION) 
    print("Number of boids to render: ", boids_total)
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
        
        for subhorde, update_params in horde:
            # Update boids
            subhorde.update(*update_params)
            # Draw boids
            subhorde.draw(screen)

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
                        f"{boids_total}_boids_{settings["number_of_species"]}_species_" + \
                        f"{settings["length_in_seconds"]}s_animation.gif")
    # Numarate image
    counter = 1
    while os.path.exists(name):
        name = os.path.join(parent_dir, "Animations",
                f"{boids_total}_boids_{settings["length_in_seconds"]}s_animation({counter}).gif")
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
    input("\nPress [Enter] to come back to main menu.")

    # Quit Pygame and come back to main script
    pygame.quit()

