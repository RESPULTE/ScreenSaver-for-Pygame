import pygame

def draw_grid(surf, grid_size: tuple, grid_color):
    grid_w, grid_h = grid_size
    surf_w, surf_h = surf.get_size()
    # draw grid lines
    # if the line is being drawn at the last position for x or y axis
    # offset it by 5 pixel, or else it'll be drawn out of bound and it'll not be visible
    for row in range(0, surf_h + 1, grid_h):
        if row != surf_h:
            pygame.draw.line(surf, grid_color, (0, row), (surf_w, row), 5)
            continue
        pygame.draw.line(surf, grid_color, (0, row - 5), (surf_w, row - 5), 5)

    for col in range(0,surf_w + 1, grid_w):
        if col !=surf_w:
            pygame.draw.line(surf, grid_color, (col, 0), (col, surf_h), 5)
            continue
        pygame.draw.line(surf, grid_color, (col - 5, 0), (col - 5, surf_h), 5)

    return surf

def resize_surf(surf, window: pygame.Surface = None, size: tuple = None, ratio: tuple = None):
    if len([bool(x) for x in [window, size, ratio]]) > 1:
        raise ValueError(f"only accepts 1 arguement at a time!")
    surf_w, surf_h = surf.get_size()
    if window:
        win_w, win_h = win.get_size()
        ratio_w = win_w / surf_w
        ratio_h = win_h / surf_h
        win_ratio = min(ratio_w, ratio_h)
        surf = pygame.transform.scale(surf, (int(surf_w * win_ratio), int(surf_h * win_ratio))) 
    if ratio:
        surf = pygame.transform.scale(surf, (int(surf_w * ratio[0]), int(surf_h * ratio[1]))) 
    if size:
        surf = pygame.transform.scale(surf, size) 

    return surf

def horizontal_flip(surf):
    return pygame.transform.flip(surf, xbool=True)

def vertical_flip(surf):
    return pygame.transform.flip(surf, ybool=True)

def decrease_surf_alpha(surf, decrement: int):
    alpha = surf.get_alpha()
    surf.set_alpha(max(alpha - decrement, 0))
    return surf

def create_surf(surfSize, surfColor, flag):
    surf = pygame.Surface((surfSize), flag)
    surf.fill(surfColor)

    return surf


class Button:

    def __init__(self, rect):
        self._rect = pygame.Rect(rect)

        self._hovering = False 
        self._clicked  = False  

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, newRect):
        self._rect = newRect

    def check_state(self, state: str):
        assert state == 'hovering' or state == 'clicked' 
        state_ = getattr(self, state)
        setattr(self, state, False)
        return state_

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self._hovering = True if self._rect.collidepoint(mouse_pos) else False

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._clicked = True