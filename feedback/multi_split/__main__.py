"""Facility for image visualization."""

### standard library import
from itertools import cycle


### thrid-party imports

## pygame

from pygame import QUIT, KEYUP, K_ESCAPE, Surface, Rect

from pygame.display import get_surface, update
from pygame.time    import Clock
from pygame.math    import Vector2
from pygame.event   import get as get_events
from pygame.image   import fromstring as image_from_string
from pygame.draw    import rect as draw_rect


## Pillow
from PIL.Image import Image


### get screen and its rect

screen      = get_surface()
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


def multi_split_view(

      *images: Image,

      axis_to_split: {
        'widget_name': 'option_tray',
        'widget_kwargs': {
          'options': ['X', 'Y'],
        },
        'type': str,
      } = 'X',

    ):
    """Display image centered on screen, then return it.

    To stop displaying the image just press <Escape>.
    This will trigger the exit of the inner loop.
    """
    ### raise error if no images are given

    if not images:

        raise ValueError(
                "No images were received."
              )

    ### if check pattern wasn't draw yet on background,
    ### do so now

    if MUST_DRAW_CHECKER_PATTERN:

        _blit_checker_pattern(background)
        MUST_DRAW_CHECKER_PATTERN.pop()

    ### obtain surfaces from pillow images

    surfs = [
      _surf_from_pillow_image(image)
      for image in images
    ]

    n = len(surfs)

    rect   = surfs[0].get_rect()
    canvas = Surface(rect.size).convert()

    (
      dimension_to_split,
      index_to_increment,
    ) = (

      (
        'height',
        1,
      )
      if axis_to_split.lower() == 'y'

      else (
        'width',
        0,
      )

    )

    value = getattr(rect, dimension_to_split)
    pixels_per_split, remainder = divmod(value, n)

    split_values = [pixels_per_split] * n
    split_values[-1] += remainder

    split_rect = rect.copy()

    for surf, split_value in (
      zip(surfs, split_values)
    ):
        
        setattr(
          split_rect,
          dimension_to_split,
          split_value
        )

        canvas.blit(
                 surf.subsurface(split_rect),
                 split_rect,
               )

        split_rect[index_to_increment] += split_value

    ### clean the screen
    screen.blit(background, (0, 0))

    ### center image rect on the screen
    rect.center = screen_center

    ### blit image center on the screen using the rect
    screen.blit(canvas, rect)

    ### loop support

    running = True

    ### start loop

    while running:

        maintain_fps(30)
        
        for event in get_events():

            if event.type == QUIT: running = False

            elif (

                  event.type == KEYUP
              and event.key  == K_ESCAPE

            ):

                running = False

        ### update screen
        update()


multi_split_view.dismiss_exec_time_tracking = True

main_callable = multi_split_view
