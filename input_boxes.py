"""InputBox class for handling parameter changes"""

import pygame

class InputBox:
    """
    """
    def __init__(self, initial_value: float,
                 x: int, y: int, 
                 w: int=400, h: int=50, 
                 name: str='', 
                 active_color: tuple[int, int, int]=(10, 10, 200),
                 inactive_color: tuple[int, int, int]=(30, 30, 100)) -> None:
        
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
        screen.blit(self.name_surface, (self.rect.x, self.rect.y - 30))
        pygame.draw.rect(screen, self.color, self.rect, 4)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
