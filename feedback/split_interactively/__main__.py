"""Facility for image visualization."""

### standard library imports

from itertools import cycle

from types import SimpleNamespace



### thrid-party imports

## pygame

from pygame import (

              QUIT, KEYUP, K_ESCAPE,
              MOUSEBUTTONDOWN, MOUSEBUTTONUP,

              Surface, Rect,
            )

from pygame.display import get_surface, update
from pygame.time    import Clock
from pygame.math    import Vector2
from pygame.event   import get as get_events
from pygame.image   import fromstring as image_from_string

from pygame.mouse import (
                    get_pos as get_mouse_pos,
                    set_pos as set_mouse_pos,
                  )

from pygame.transform import rotate as rotate_surface

from pygame.draw import (
                   rect   as draw_rect,
                   line   as draw_line,
                   lines  as draw_lines,
                   circle as draw_circle,
                 )


## Pillow
from PIL.Image import Image


NS = SimpleNamespace()



### get screen and its rect

screen      = get_surface()
screen_copy = screen.copy()
screen_rect = screen.get_rect()

### get a vector for the center of the screen
screen_center = Vector2(screen_rect.center)

### instantiate background
background = Surface(screen.get_size()).convert()

### obtain fps maintaining operation
maintain_fps = Clock().tick

### create a flag to determine whether we must draw a
### a checker pattern on the background (in case we didn't
### do so yet)
MUST_DRAW_CHECKER_PATTERN = [None]


def _blit_checker_pattern(surf):
    """Blit checker pattern on surf with colors and rect."""
    ### define settings

    color_a = (235, 235, 235)
    color_b = (120, 120, 120)

    rect_width  = 40
    rect_height = 40

    ### retrieve a rect from the surf
    surf_rect = surf.get_rect()

    ### create a color cycler from the received colors
    next_color = cycle((color_a, color_b)).__next__

    ### create a rect with the provided dimensions, called
    ### unit rect, since it represents an unit or tile in
    ### the checker pattern
    unit_rect = Rect(0, 0, rect_width, rect_height)

    ### use the unit rect width and height as offset
    ### amounts in the x and y axes

    x_offset = rect_width
    y_offset = rect_height

    ### "walk" the surface while blitting the checker
    ### pattern until the surface the entire area of
    ### the surface is covered by the checker pattern

    while True:
        
        ## if the unit rect isn't touching the
        ## surface area, invert the x_offset,
        ## move it back using such new x_offset and
        ## move it down using the y_offset

        if not surf_rect.colliderect(unit_rect):
            x_offset = -x_offset
            unit_rect.move_ip(x_offset, y_offset)

        ## if even after the previous if block the
        ## unit rect still doesn't touch the surface
        ## area, break out of the while loop
        if not surf_rect.colliderect(unit_rect): break

        ## draw the rect
        draw_rect(surf, next_color(), unit_rect)

        ## move the unit rect in the x axis using the
        ## x_offset
        unit_rect.move_ip(x_offset, 0)


def _surf_from_pillow_image(image):

    mode = image.mode
    size = image.size
    data = image.tobytes()

    return image_from_string(data, size, mode)

### create split widgets

X_SPLIT_SURF = Surface((30, 30)).convert_alpha()
X_SPLIT_SURF.fill((0, 0, 0, 0))
icon_rect = X_SPLIT_SURF.get_rect()

sm_rect = icon_rect.inflate(-10, -10)
xs_rect = icon_rect.inflate(-20, -20)

draw_circle(
  X_SPLIT_SURF,
  (255, 255, 255),
  icon_rect.center,
  15,
)

for attr_names in (

  (
    'topleft',
    'midleft',
    'bottomleft',
  ),

  (
    'topright',
    'midright',
    'bottomright',
  ),

):
    
    attr_name1, attr_name2, attr_name3 = attr_names

    points = (
      getattr(xs_rect, attr_name1),
      getattr(sm_rect, attr_name2),
      getattr(xs_rect, attr_name3),
    )

    draw_lines(
      X_SPLIT_SURF,
      (0, 0, 255),
      False,
      points,
      3,
    )

Y_SPLIT_SURF = rotate_surface(X_SPLIT_SURF, 90)

class SplitWidget:

    def __init__(self, axis_to_split):

        self.set_axis(axis_to_split)
        self.rect = self.image.get_rect()

    def set_axis(self, axis_to_split):

        self.axis_to_split = axis_to_split.lower()
        
        if self.axis_to_split == 'x':

            self.image = X_SPLIT_SURF
            self.draw_line = self.draw_y_axis
            self.get_factor = self.get_x_factor

        else:

            self.image = Y_SPLIT_SURF
            self.draw_line = self.draw_x_axis
            self.get_factor = self.get_y_factor

    def draw_x_axis(self):

        draw_line(
          screen,
          (255, 255, 0),
          (screen_rect.left, self.rect.centery),
          (screen_rect.right, self.rect.centery),
          3,
        )

    def draw_y_axis(self):

        draw_line(
          screen,
          (255, 255, 0),
          (self.rect.centerx, screen_rect.top),
          (self.rect.centerx, screen_rect.bottom),
          3,
        )

    def get_x_factor(self):

        return (
          (self.rect.centerx - self.rect_ref.left)
          / self.rect_ref.width
        )

    def get_y_factor(self):

        return (
          (self.rect.centery - self.rect_ref.top)
          / self.rect_ref.height
        )

    def handle_events(self):
        
        for event in get_events():

            if event.type == QUIT: running = False

            elif (

                  event.type == KEYUP
              and event.key  == K_ESCAPE

            ):

                NS.running = False

            elif (
                  event.type   == MOUSEBUTTONUP
              and event.button == 1
            ):

                NS.loop_holder = NORMAL_STATE
                self.perform_split()

    def update(self):

        mouse_pos = get_mouse_pos()

        if self.rect_ref.collidepoint(mouse_pos):
            self.rect.center = mouse_pos

    def draw(self):

        screen.blit(screen_copy, (0, 0))

        self.draw_line()

        screen.blit(self.image, self.rect)

        update()

    def perform_split(self):

        surf = self.surf_ref
        rect = surf.get_rect()

        if self.axis_to_split == 'y':
            #rect.size = rect.h, rect.w
            rect.size = (*reversed(rect.size),)

        rect1 = rect.copy()
        rect2 = rect.copy()

        rect1.w *= self.get_factor()
        rect2.w  = rect.w - rect1.w

        if self.axis_to_split == 'y':

            for r in (rect, rect1, rect2):
                r.size = (*reversed(r.size),)

            rect2.topleft = rect1.bottomleft

        else: rect2.topleft = rect1.topright

        surf.blit(self.surf1.subsurface(rect1), rect1)
        surf.blit(self.surf2.subsurface(rect2), rect2)

        ### clean the screen
        screen.blit(background, (0, 0))

        ### center image rect on the screen
        rect.center = screen_center

        ### blit image center on the screen using the rect
        screen.blit(surf, rect)

        ### blit screen into its copy
        screen_copy.blit(screen, (0, 0))

        ### execute draw method
        self.draw()

SPLIT_WIDGET = SplitWidget('x')

###

class NormalState:

    def handle_events(self):
        
        for event in get_events():

            if event.type == QUIT: running = False

            elif (

                  event.type == KEYUP
              and event.key  == K_ESCAPE

            ):

                NS.running = False

            elif (
                  event.type   == MOUSEBUTTONDOWN
              and event.button == 1
            ):
                
                if SPLIT_WIDGET.rect.collidepoint(event.pos):

                    set_mouse_pos(SPLIT_WIDGET.rect.center)
                    NS.loop_holder = SPLIT_WIDGET

    def update(self): pass

    def draw(self):
        update()

NORMAL_STATE = NormalState()

###

def split_interactively(

      image1: Image,
      image2: Image,

      axis_to_split: {
        'widget_name': 'option_tray',
        'widget_kwargs': {
          'options': ['X', 'Y'],
        },
        'type': str,
      } = 'X',

    ):
    """Display image centered on screen.

    To stop displaying the image just press <Escape>.
    This will trigger the exit of the inner loop.
    """
    ### if check pattern wasn't draw yet on background,
    ### do so now

    if MUST_DRAW_CHECKER_PATTERN:

        _blit_checker_pattern(background)
        MUST_DRAW_CHECKER_PATTERN.pop()

    ### set split widget axis and center it

    SPLIT_WIDGET.set_axis(axis_to_split)
    SPLIT_WIDGET.rect.center = screen_rect.center

    ### obtain surfaces from pillow images

    SPLIT_WIDGET.surf1 = _surf_from_pillow_image(image1)
    SPLIT_WIDGET.surf2 = _surf_from_pillow_image(image2)

    surf = Surface(image1.size).convert()
    SPLIT_WIDGET.surf_ref = surf

    rect_ref = surf.get_rect()
    rect_ref.center = screen_rect.center

    SPLIT_WIDGET.rect_ref = rect_ref

    SPLIT_WIDGET.perform_split()

    ### loop support

    loop_holder = NS.loop_holder = NORMAL_STATE
    running     = NS.running     = True

    ### start loop

    while running:

        maintain_fps(30)

        loop_holder.handle_events()
        loop_holder.update()
        loop_holder.draw()

        loop_holder = NS.loop_holder
        running     = NS.running


split_interactively.dismiss_exec_time_tracking = True

main_callable = split_interactively
