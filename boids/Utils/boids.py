"""
Horde Class for Boids Simulation

This module defines the `Horde` class, which represents a collection of boids in a 2D simulation.
Each boid exhibits flocking behaviors such as separation, alignment, and cohesion. The `Horde` class 
manages the positions, velocities, sizes, and colors of the boids and provides methods for updating 
their states and rendering them on a Pygame surface.

Key Features:
- Dynamic boid behavior influenced by separation, alignment, and cohesion forces.
- Customizable colors and visual styles, including predefined schemes and constant RGB values.
- Collision avoidance and boundary handling using edge factors and margins.
- Efficient drawing of rotated boids based on their velocity directions.

Dependencies:
- `pygame` for visualization.
- `numpy` for efficient mathematical computations.
"""

import pygame
import math
import numpy as np

class Horde():
    """
    Represents a collection of boids with customizable behavior and visual properties.

    The `Horde` class manages the state and behavior of a group of boids. It allows for:
    - Adding new boids with specific positions, velocities, and sizes.
    - Updating boid states based on flocking rules (separation, alignment, and cohesion).
    - Handling boundary interactions to ensure boids stay within specified edges.
    - Rendering boids on a Pygame surface with rotation and customizable colors.

    Attributes:
        positions (np.ndarray): Array of shape (N, 2) containing boid positions.
        velocities (np.ndarray): Array of shape (N, 2) containing boid velocities.
        sizes (np.ndarray): Array of shape (N,) containing boid sizes.
        colors (np.ndarray): Array of shape (N, 3) containing RGB color values.
        color (str): Color scheme for the boids. Options include "green-purple", 
            "purple-green", "black&white", or a constant RGB value specified as "const R G B".

    Example Usage:
        >>> import pygame
        >>> from boids import Horde

        >>> # Initialize Pygame and create a display surface
        >>> pygame.init()
        >>> screen = pygame.display.set_mode((1280, 720))

        >>> # Create a Horde with a green-purple color scheme
        >>> horde = Horde(color_type="green-purple")

        >>> # Add boids to the horde
        >>> horde.add_boid(position=(100.0, 200.0), velocity=(1.0, -0.5), size=20)
        >>> horde.add_boid(position=(300.0, 400.0), velocity=(-1.0, 0.5), size=25)

        >>> # Update and draw the boids in a loop
        >>> running = True
        >>> while running:
        >>>     for event in pygame.event.get():
        >>>         if event.type == pygame.QUIT:
        >>>             running = False
        >>>     
        >>>     # Clear the screen
        >>>     screen.fill((0, 0, 0))

        >>>     # Update and draw the horde
        >>>     horde.update(
        >>>         separation_factor=0.005, separation_distance=60,
        >>>         alignment_factor=0.06, alignment_distance=90,
        >>>         cohesion_factor=0.005, edge_factor=0.005,
        >>>         top_speed=5, bottom_speed=1,
        >>>         edges=(80, 1200, 80, 640), margin=50
        >>>     )
        >>>     horde.draw(screen)

        >>>     # Update the display
        >>>     pygame.display.flip()

        >>> # Quit Pygame
        >>> pygame.quit()
    """

    def __init__(self, color_type: str) -> None:
        """
        Initializes a Horde instance with the specified color scheme.

        Args:
            color_type (str): The color scheme for the boids. Available options:
                - "green-purple": Default color scheme.
                - "purple-green": Reverse of the default color scheme.
                - "black&white": Boids are brighter in groups.
                - "const R G B": A constant RGB value for all boids, where R, G, B are integers (0-255).

        Example:
            horde = Horde(color_type="green-purple")
        """
        self.positions: np.ndarray = np.empty((0, 2), dtype=np.float32)
        self.velocities: np.ndarray = np.empty((0, 2), dtype=np.float32)
        self.sizes: np.ndarray = np.empty(0, dtype=np.uint16)
        self.colors: np.ndarray = np.empty((0, 3), dtype=np.uint8)
        self.color: str = color_type
    
    def add_boid(self, position: tuple[float, float], velocity: tuple[float, float], size: int = 25):
        """
        Adds a new boid to the horde with the specified position, velocity, and size.

        Args:
            position (tuple[float, float]): The (x, y) coordinates of the boid.
            velocity (tuple[float, float]): The initial velocity vector of the boid.
            size (int, optional): The size (radius) of the boid. Defaults to 25.

        Example:
            horde.add_boid(position=(100.0, 200.0), velocity=(1.0, -0.5), size=20)
        """
        # Convert position and velocity to numpy arrays and append them
        position_np = np.array(position, dtype=np.float32).reshape(1, 2)
        velocity_np = np.array(velocity, dtype=np.float32).reshape(1, 2)
        default_color = np.array([10, 150, 10], dtype=np.uint8).reshape(1, 3)
        
        # Update arrays
        self.positions = np.vstack((self.positions, position_np))
        self.velocities = np.vstack((self.velocities, velocity_np))
        self.sizes = np.append(self.sizes, size)
        self.colors = np.vstack((self.colors, default_color))

    def update(self, 
               separation_factor: float, separation_distance: int,
               alignment_factor: float, alignment_distance: int,
               cohesion_factor: float, edge_factor: int,
               top_speed: int, bottom_speed: int,
               edges: tuple[int, int, int, int] = (80, 1840, 80, 1000),
               margin: int = 100) -> None:
        """
        Updates the positions, velocities, and states of all boids in the horde.

        Args:
            separation_factor (float): Weight for separation behavior.
            separation_distance (int): Distance threshold for separation behavior.
            alignment_factor (float): Weight for alignment behavior.
            alignment_distance (int): Distance threshold for alignment behavior.
            cohesion_factor (float): Weight for cohesion behavior.
            edge_factor (int): Weight for edge avoidance forces.
            top_speed (int): Maximum speed for the boids.
            bottom_speed (int): Minimum speed for the boids.
            edges (tuple[int, int, int, int], optional): Boundary edges (left, right, top, bottom). Defaults to (80, 1840, 80, 1000).
            margin (int, optional): Margin distance for edge avoidance. Defaults to 100.

        Example:
            horde.update(0.005, 60, 0.06, 90, 0.005, 0.005, 5, 1)
        """
        # Compute pairwise distances between boids
        distances = np.linalg.norm(self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :], axis=-1)

        # Initialize changes
        separation_change = np.zeros_like(self.velocities)
        alignment_change = np.zeros_like(self.velocities)
        cohesion_change = np.zeros_like(self.velocities)

        # Counters for color adjustments
        separation_counters = np.zeros(len(self.positions), dtype=np.int32)
        alignment_counters = np.zeros(len(self.positions), dtype=np.int32)

        # Update each boid based on its neighbors
        for i in range(len(self.positions)):
            neighbors_horde = distances[i] < alignment_distance
            separation_horde = distances[i] < separation_distance
            alignment_counters[i] = np.sum(neighbors_horde)
            separation_counters[i] = np.sum(separation_horde)

            # Separation: avoid boids that are too close
            separation_change[i] = np.sum(self.positions[i] - self.positions[separation_horde], axis=0)
            #if np.any(separation_horde):
             #   close_boids = distances[i] < (separation_distance * 0.5)
              #  separation_change[i] += np.sum(self.positions[i] - self.positions[close_boids], axis=0) * (separation_factor * 1.5)

            # Alignment: match velocity of nearby boids
            alignment_change[i] = np.mean(self.velocities[neighbors_horde], axis=0) - self.velocities[i]

            # Cohesion: move towards the center of mass of nearby boids
            cohesion_change[i] = np.mean(self.positions[neighbors_horde], axis=0) - self.positions[i]
        
        # Apply the computed changes with the respective factors
        self.velocities += separation_change * separation_factor + \
                           alignment_change * alignment_factor + \
                           cohesion_change * cohesion_factor

        # Update positions
        self.positions += self.velocities

        # Update colors
        self._update_colors(alignment_counters, separation_counters)

        # Edge force
        left, right, top, bottom = edges
        near_left_edge = self.positions[:, 0] < left + margin
        near_right_edge = self.positions[:, 0] > right - margin
        near_top_edge = self.positions[:, 1] < top + margin
        near_bottom_edge = self.positions[:, 1] > bottom - margin
        self.velocities[near_left_edge, 0] += edge_factor * ((left + margin) - self.positions[near_left_edge, 0])
        self.velocities[near_right_edge, 0] -= edge_factor * (self.positions[near_right_edge, 0] - (right - margin))
        self.velocities[near_top_edge, 1] += edge_factor * ((top + margin) - self.positions[near_top_edge, 1])
        self.velocities[near_bottom_edge, 1] -= edge_factor * (self.positions[near_bottom_edge, 1] - (bottom - margin))

        # Edge block
        self.positions[:, 0] = np.clip(self.positions[:, 0], left, right)
        self.positions[:, 1] = np.clip(self.positions[:, 1], top, bottom)

        # Ensure boids stay within the speed range
        speeds = np.linalg.norm(self.velocities, axis=1)
        self.velocities[speeds > top_speed] *= top_speed / speeds[speeds > top_speed][:, np.newaxis]
        self.velocities[speeds < bottom_speed] *= bottom_speed / speeds[speeds < bottom_speed][:, np.newaxis]
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws all boids in the horde onto the given Pygame surface.

        Each boid is rotated based on its velocity direction and rendered with its current color.

        Args:
            screen (pygame.Surface): The Pygame surface on which to render the boids.

        Example:
            horde.draw(screen)
        """
        for i, (pos, vel, size) in enumerate(zip(self.positions, self.velocities, self.sizes)):
            # Cache or create a boid surface once for each size
            boid_surface= self._create_boid_surface(size, self.colors[i])
            
            # Rotate the surface based on the boid's velocity direction
            rotation_angle = math.degrees(math.atan2(vel[1], vel[0]))
            rotated_surface = pygame.transform.rotate(boid_surface, -rotation_angle)
            
            # Adjust the position of the boid based on the rotated surface size
            rotated_rect = rotated_surface.get_rect(center=(pos[0], pos[1]))
            
            # Blit (draw) the rotated boid surface onto the screen
            screen.blit(rotated_surface, rotated_rect)

    def _create_boid_surface(self, size: int, color: tuple[int, int, int]) -> tuple[pygame.Surface, pygame.Rect]:
        # Create a new surface with transparency
        boid_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Define the shape of the boid
        half_size = size / 2
        quarter_size = size / 4
        points = [
            (-half_size, -quarter_size),
            (half_size, 0),
            (-half_size, quarter_size),
            (-quarter_size, 0)
        ]
        
        shifted_points = [(x + half_size, y + half_size) for x, y in points]
        pygame.draw.polygon(boid_surface, color, shifted_points)

        return boid_surface

    def _update_colors(self, counters: np.ndarray, separation_counters: np.ndarray) -> None:
        """
        Updates the colors of all boids based on the current color scheme.

        Args:
            counters (np.ndarray): Array representing the alignment neighbor counts for each boid.
            separation_counters (np.ndarray): Array representing the separation neighbor counts for each boid.

        Color Schemes:
            - "green-purple": Default scheme.
            - "purple-green": Reverse of the default scheme.
            - "black&white": Brightness increases with grouping.
            - "const R G B": Constant RGB values for all boids.

        Example:
            horde._update_colors(counters, separation_counters)
        """
        if self.color == "green-purple":
            red = np.clip(separation_counters * 16, 0, 255)
            green = np.clip(255 - counters * 2, 0, 255)
            blue = np.clip(255 - green, 0, 255)
            self.colors[:, 0] = red
            self.colors[:, 1] = green
            self.colors[:, 2] = blue
        elif self.color == "purple-green":
            red = np.clip(255 - separation_counters * 16, 0, 255)
            green = np.clip(counters * 2, 0, 255)
            blue = np.clip(green, 0, 255)
            self.colors[:, 0] = red
            self.colors[:, 1] = green
            self.colors[:, 2] = blue
        elif self.color.startswith("const"):
            r, g, b = [int(x) for x in self.color.split()[1:]]
            self.colors[:, 0] = r
            self.colors[:, 1] = g
            self.colors[:, 2] = b
        elif self.color == "black&white":
            rgb = np.clip(counters * 32, 0, 255)
            self.colors[:, 0] = rgb
            self.colors[:, 1] = rgb
            self.colors[:, 2] = rgb
