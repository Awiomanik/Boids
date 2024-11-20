"""
InputBox Class for Parameter Adjustments in Pygame

This module defines the `InputBox` class, a utility for managing user input in a graphical Pygame application.
The `InputBox` is designed to capture numeric values from the user and display them interactively, 
with features like highlighting when active and validation upon submission.

Key Features:
    - Displays parameter name and current value.
    - Supports numeric input and validates entered values.
    - Visual feedback for active and inactive states.

Dependencies:
    - `pygame`: For rendering and handling events.

Example Usage:
    - Create an instance of `InputBox` with initial values and position.
    - Call `handle_event()` for every event to process user interactions.
    - Call `draw()` to render the input box and its label on the Pygame surface.
"""

import pygame

class InputBox:
    """
    A graphical input box for capturing numeric parameters in Pygame.

    The `InputBox` class provides an interactive interface for users to adjust numeric parameters 
    in real-time. It displays the parameter name, the current value, and supports editing with 
    validation for numeric input.

    Attributes:
        val (float): The current value of the parameter.
        rect (pygame.Rect): The rectangle defining the input box's position and size.
        a_color (tuple[int, int, int]): Color when the input box is active.
        i_color (tuple[int, int, int]): Color when the input box is inactive.
        color (tuple[int, int, int]): Current color based on active state.
        text (str): The text representation of the current value.
        txt_surface (pygame.Surface): Rendered text surface for the current value.
        name (str): The name of the parameter displayed above the input box.
        name_surface (pygame.Surface): Rendered text surface for the parameter name.
        active (bool): Indicates whether the input box is currently active.

    Example Usage:
        >>> input_box = InputBox(initial_value=1.5, x=100, y=200, name="Parameter")
        >>> for event in pygame.event.get():
        >>>     input_box.handle_event(event)
        >>> input_box.draw(screen)
    """
    def __init__(self, initial_value: float,
                 x: int, y: int, 
                 w: int=400, h: int=50, 
                 name: str='', 
                 active_color: tuple[int, int, int]=(10, 10, 200),
                 inactive_color: tuple[int, int, int]=(30, 30, 100)) -> None:
        """
        Initializes an InputBox instance.

        Args:
            initial_value (float): The initial numeric value of the parameter.
            x (int): The x-coordinate of the input box's top-left corner.
            y (int): The y-coordinate of the input box's top-left corner.
            w (int, optional): The width of the input box. Defaults to 400.
            h (int, optional): The height of the input box. Defaults to 50.
            name (str, optional): The name of the parameter displayed above the input box. Defaults to an empty string.
            active_color (tuple[int, int, int], optional): The color of the box when active. Defaults to (10, 10, 200).
            inactive_color (tuple[int, int, int], optional): The color of the box when inactive. Defaults to (30, 30, 100).

        Example:
            input_box = InputBox(1.0, 100, 200, name="Example Parameter")
        """
        
        self.val: float = initial_value
        self.rect: pygame.Rect = pygame.Rect(x, y, w, h)
        self.a_color: tuple[int, int, int] = active_color
        self.i_color: tuple[int, int, int] = inactive_color
        self.color: tuple[int, int, int] = self.i_color
        self.text: str = str(self.val)
        self.txt_surface: pygame.Surface = pygame.font.Font(None, 40).render(self.text, True, self.color)
        self.name: str = name
        self.name_surface: pygame.Surface = pygame.font.Font(None, 40).render(self.name, True, self.a_color)
        self.active = False

    def handle_event(self, event: pygame.event) -> None:
        """
        Handles user interactions with the input box.

        Processes mouse and keyboard events to toggle the active state of the input box 
        and update its value based on user input. Supports numeric validation for entered values.

        Args:
            event (pygame.event): A Pygame event object to process user input.

        Behavior:
            - Left-click toggles the active state of the input box.
            - Pressing `Enter` validates the current input and updates the value.
            - Typing updates the displayed text; `Backspace` deletes characters.

        Example:
            for event in pygame.event.get():
                input_box.handle_event(event)
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle the active variable if the user clicked on the input_box.
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
                self.color = self.i_color
            # Change the current color of the input box.
            self.color = self.a_color if self.active else self.i_color
            # Re-render the text
            self.txt_surface = pygame.font.Font(None, 40).render(self.text, True, self.color)


        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    try:
                        self.val = float(self.text)
                        if self.active:
                            self.active = False
                            self.color = self.i_color
                    except:
                        self.text = str(self.val)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = pygame.font.Font(None, 40).render(self.text, True, self.color)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Renders the input box and its label on the specified Pygame surface.

        Args:
            screen (pygame.Surface): The Pygame surface on which to draw the input box.

        Behavior:
            - Displays the parameter name above the input box.
            - Draws the input box with the current color and text.

        Example:
            input_box.draw(screen)
        """
        screen.blit(self.name_surface, (self.rect.x, self.rect.y - 30))
        pygame.draw.rect(screen, self.color, self.rect, 4)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
