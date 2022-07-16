"""Facility for image visualization."""

### standard library import
from itertools import cycle


### thrid-party imports

## pygame

from pygame import (

              QUIT,

              KEYUP,

              K_ESCAPE,

              K_w, K_a, K_s, K_d,
              K_UP, K_LEFT, K_DOWN, K_RIGHT,

              Surface, Rect,

            )

from pygame.display import get_surface, update
from pygame.time    import Clock
from pygame.event   import get as get_events
from pygame.image   import fromstring as image_from_string
from pygame.draw    import rect as draw_rect

from pygame.key import get_pressed as get_pressed_keys


## Pillow
from PIL.Image import Image



### get screen and its rect

SCREEN      = get_surface()
SCREEN_RECT = SCREEN.get_rect()

### create a scroll area so the image can be moved around
SCROLL_AREA = SCREEN_RECT.inflate(-80, -80)

### define scrolling speeds in different 2D axes

X_SCROLLING_SPEED = 20
Y_SCROLLING_SPEED = 20

### instantiate background
BACKGROUND = Surface(SCREEN.get_size()).convert()

### create flag so drawing the checker pattern can be
### postponed to when the node is executed
MUST_DRAW_CHECKER_PATTERN = True


def blit_checker_pattern(surf):
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


### define function to manage scrolling the image

def manage_scrolling(image_rect):

    key_input = get_pressed_keys()

    ### calculate x movement

    if image_rect.width > SCREEN_RECT.width:

        go_left = any(
          key_input[key] for key in (K_a, K_LEFT)
        )

        go_right = any(
          key_input[key] for key in (K_d, K_RIGHT)
        )

        if (

             (go_left and go_right)
          or (not go_left and not go_right)

        ):
            x_movement = 0

        elif go_left and not go_right:
            x_movement = -1 * X_SCROLLING_SPEED

        elif go_right and not go_left:
            x_movement = 1 * X_SCROLLING_SPEED

    else: x_movement = 0

    ### apply x movement if != 0

    if x_movement < 0:

        if (
          (image_rect.right + x_movement)
          < SCROLL_AREA.right
        ):
            image_rect.right = SCROLL_AREA.right

        else: image_rect.x += x_movement

    elif x_movement > 0:

        if (
          (image_rect.left + x_movement)
          > SCROLL_AREA.left
        ):
            image_rect.left = SCROLL_AREA.left

        else: image_rect.x += x_movement

    ### calculate y movement

    if image_rect.height > SCREEN_RECT.height:

        go_up = any(
          key_input[key] for key in (K_w, K_UP)
        )

        go_down = any(
          key_input[key] for key in (K_s, K_DOWN)
        )

        if (

             (go_up and go_down)
          or (not go_up and not go_down)

        ):
            y_movement = 0

        elif go_up and not go_down:
            y_movement = -1 * Y_SCROLLING_SPEED

        elif go_down and not go_up:
            y_movement = 1 * Y_SCROLLING_SPEED

    else: y_movement = 0

    ### apply y movement if != 0

    if y_movement < 0:

        if (
          (image_rect.bottom + y_movement)
          < SCROLL_AREA.bottom
        ):
            image_rect.bottom = SCROLL_AREA.bottom

        else: image_rect.y += y_movement

    elif y_movement > 0:

        if (
          (image_rect.top + y_movement)
          > SCROLL_AREA.top
        ):
            image_rect.top = SCROLL_AREA.top

        else: image_rect.y += y_movement


### define function to watch out for window resizing
### and perform needed setups when it is the case

def watch_window_size(image_surf, image_rect):

    global BACKGROUND

    ### if the screen and the background have the
    ### same size, then no window resizing took place,
    ### so we exit the function right away
    if SCREEN.get_size() == BACKGROUND.get_size(): return

    ### other, we keep executing the function, performing
    ### the window resize setups

    ## update the screen rect's size
    SCREEN_RECT.size = SCREEN.get_size()

    ## center the image on the screen
    image_rect.center = SCREEN_RECT.center

    ## recreate the background

    BACKGROUND = (

      Surface(SCREEN.get_size()).convert()

    )

    ## redraw the checker pattern on the background
    blit_checker_pattern(BACKGROUND)

    ## clean the screen
    SCREEN.blit(BACKGROUND, (0, 0))

    ## blit image on the screen using its rect
    SCREEN.blit(image_surf, image_rect)

    ## replace the scroll area

    global SCROLL_AREA
    SCROLL_AREA = SCREEN_RECT.inflate(-80, -80)


def view_image(image: Image):
    """Display image centered on screen.

    To stop displaying the image just press <Escape>.
    This will trigger the exit of the inner loop.
    """
    ### draw the checker pattern on the background if
    ### needed

    global MUST_DRAW_CHECKER_PATTERN

    if MUST_DRAW_CHECKER_PATTERN:

        ### draw the checker pattern on the background
        blit_checker_pattern(BACKGROUND)

        ### set flag to false
        MUST_DRAW_CHECKER_PATTERN = False


    ### obtain surface from pillow image

    mode = image.mode
    size = image.size
    data = image.tobytes()

    surf = image_from_string(data, size, mode)

    ### clean the screen
    SCREEN.blit(BACKGROUND, (0, 0))

    ### get rect for image and center it on the screen

    rect = surf.get_rect()

    rect.center = SCREEN_RECT.center

    ### blit image on the screen using its rect
    SCREEN.blit(surf, rect)

    ### create variable to track topleft position
    last_topleft = rect.topleft

    ### timing support

    clock = Clock()
    running = True

    ### start loop

    while running:

        clock.tick(30)

        watch_window_size(surf, rect)
        
        ### handle events

        for event in get_events():

            if event.type == QUIT: running = False

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    running = False

        ### manage scrolling
        manage_scrolling(rect)

        ### if image moved, redraw

        if last_topleft != rect.topleft:

            last_topleft = rect.topleft

            ### clean the screen
            SCREEN.blit(BACKGROUND, (0, 0))

            ### blit image on the screen using its rect
            SCREEN.blit(surf, rect)

        ### update screen
        update()


view_image.dismiss_exec_time_tracking = True

main_callable = view_image
