"""Boids class"""

import pygame
import math
import numpy as np

class Horde():
    """
    """

    def __init__(self) -> None:
        self.positions: np.ndarray = np.empty((0, 2), dtype=np.float32)
        self.velocities: np.ndarray = np.empty((0, 2), dtype=np.float32)
        self.sizes: np.ndarray = np.empty(0, dtype=np.uint16)
        self.colors: np.ndarray = np.empty((0, 3), dtype=np.uint8)
    
    def add_boid(self, position: tuple[float, float], velocity: tuple[float, float], size: int = 25):
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
        self.update_colors(alignment_counters, separation_counters)

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
    
    def draw(self, screen: pygame.Surface) -> None:
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

    def update_colors(self, counters: np.ndarray, separation_counters: np.ndarray) -> None:
        red = np.clip(separation_counters * 16, 0, 255)
        green = np.clip(255 - counters * 2, 0, 255)
        blue = np.clip(255 - green, 0, 255)
        self.colors[:, 0] = red
        self.colors[:, 1] = green
        self.colors[:, 2] = blue
