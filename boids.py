"""Boids class"""

import pygame
import math

class Boid():
    """
    """

    def __init__(self, 
                 position: tuple[float, float], 
                 speed: tuple[float, float] = 10,
                 size: int = 25,
                 color: tuple[int, int, int] = (10, 150, 10)) -> None:
        
        self.x, self.y = position
        self.vx, self.vy = speed
        self.size: int = size
        self.color: tuple[int, int, int] = color

    def update_pos(self) -> None:
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen: pygame.Surface):
        # Define the shape of the deltoid arrow using relative points
        half_size = self.size / 2
        quater_size = self.size / 4
        points = [
            (-half_size, -quater_size),
            (half_size, 0),
            (-half_size, quater_size),
            (-quater_size, 0)
        ]
        
        # Rotate points
        rotation_angle = math.atan2(self.vy, self.vx)
        rotated_points = []
        for x, y in points:
            rotated_x = x * math.cos(rotation_angle) - y * math.sin(rotation_angle)
            rotated_y = x * math.sin(rotation_angle) + y * math.cos(rotation_angle)
            rotated_points.append((rotated_x + self.x, rotated_y + self.y))
        
        # Draw the polygon on the screen
        pygame.draw.polygon(screen, self.color, rotated_points)


class Horde():
    """
    """

    def __init__(self) -> None:
        self.boids: list[Boid] = []
    
    def add_boid(self, position: tuple[float, float], velocity: tuple[float, float]) -> None:
        self.boids.append(Boid(position, velocity))

    def update(self, 
               separation_factor: float, separation_distance: int,
               alignment_factor: float, alignment_distance: int,
               cohesion_factor: float, edge_factor: int,
               top_speed: int, bottom_speed: int,
               edges: tuple[int, int, int, int] = (80, 1840, 80, 1000),
               margin: int = 50) -> None:
        
        for i, boid in enumerate(self.boids):
            avoidx = avoidy = \
            vx_avg = vy_avg = \
            counter = separation_counter = \
            x_avg = y_avg = \
            0.

            for j, mate in enumerate(self.boids):
                # Ommit current boid
                if i == j:
                    continue

                if math.dist((boid.x, boid.y), (mate.x, mate.y)) <= separation_distance:
                    # Separation
                    avoidx += boid.x - mate.x
                    avoidy += boid.y - mate.y 
                    separation_counter += 1
            
                if math.dist((boid.x, boid.y), (mate.x, mate.y)) <= alignment_distance:
                    counter += 1
                    
                    # Alignment
                    vx_avg += mate.vx
                    vy_avg += mate.vy

                    # Cohesion
                    x_avg += mate.x
                    y_avg += mate.y

            # Separation
            boid.vx += avoidx * separation_factor
            boid.vy += avoidy * separation_factor

            if counter > 0:
                # Alignment
                boid.vx += (vx_avg / counter - boid.vx) * alignment_factor
                boid.vy += (vy_avg / counter - boid.vy) * alignment_factor

                # Cohesion
                boid.vx += (x_avg / counter - boid.x) * cohesion_factor
                boid.vy += (y_avg / counter - boid.y) * cohesion_factor
            
            # Margin
            left, right, top, bottom = edges
            if boid.x < left + margin:
                boid.vx += edge_factor * ((left + margin) - boid.x)
            if boid.x > right - margin:
                boid.vx -= edge_factor * ((right - margin) + boid.x)
            if boid.y < top + margin:
                boid.vy += edge_factor * ((top + margin) - boid.y)
            if boid.y > bottom - margin:
                boid.vy -= edge_factor * ((bottom - margin) + boid.y)
                
            # Speed range
            speed = math.sqrt(boid.vx**2 +  boid.vy**2) 
            if speed > top_speed:
                boid.vx = (boid.vx / speed) * top_speed
                boid.vy = (boid.vy / speed) * top_speed
            if 0 < speed < bottom_speed:
                boid.vx = (boid.vx / speed) * bottom_speed
                boid.vy = (boid.vy / speed) * bottom_speed

            green = 255 - counter * 4
            red = separation_counter * 24
            boid.color = (min(red, 255), max(green, 0), min((255 - green), 255))

            # Obsticles

            # Update position of the boid
            boid.update_pos()
            
    def draw(self, screen: pygame.Surface):
        for boid in self.boids:
            boid.draw(screen)
