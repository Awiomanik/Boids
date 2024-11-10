"""
Fun with boids.
Small script to play with boids algorythms and create some fun visuals.
"""
import pygame
import sys
import random 
import gc
import os
from boids import Horde

# gif
from PIL import Image
frames = []
FRAME_DURATION = 35
animation_duration = 1
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

for i in range(5):
    coord = (float(random.randint(100, 1180)), float(random.randint(100, 620)))
    for _ in range(200):
        horde.add_boid(coord,
                    (random.randrange(-2, 2), 
                    random.randrange(-2, 2)))
print("Number of boids to render:", len(horde.positions))

# Main loop
while running:
    if len(frames) > animation_duration:
        running = False
    print("Rendering frames:", len(frames), '/', animation_duration, end='\r')

    # Draw background
    screen.fill((0, 0, 0))

    # Update boids
    horde.update(0.02, 20, 0.05, 100, 0.002, 0.01, 15, 1, (0, 1280, 0, 720))
    
    # Draw boids
    horde.draw(screen)

    frame_image = pygame.image.tostring(screen, 'RGB')
    frame_image = Image.frombytes('RGB', screen.get_size(), frame_image)
    frames.append(frame_image)

if frames:
    print("\nCreating gif...", end='\r')
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    name = os.path.join(parent_dir, f"Animations//{len(horde.positions)}_boids_animation.gif")

    counter = 1
    while os.path.exists(name):
        name = os.path.join(parent_dir, f"Animations//{len(horde.positions)}_boids_animation({counter}).gif")
        counter += 1
    
    gc.collect()
    frames[0].save(name, save_all=True, append_images=frames[1:], duration=FRAME_DURATION, loop=0)
    print("Finnished. GIF file is saved under:", name)

# Quit Pygame
pygame.quit()
import subprocess
subprocess.Popen(["python", "main.py"])
sys.exit()

