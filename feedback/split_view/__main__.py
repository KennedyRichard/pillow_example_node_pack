"""Facility for image visualization."""

### standard library import
from itertools import cycle


### third-party imports

## pygame-ce

from pygame import (

              QUIT,

              KEYUP,

              K_ESCAPE,


              K_w, K_a, K_s, K_d,
              K_UP, K_LEFT, K_DOWN, K_RIGHT,
              K_HOME,

              MOUSEBUTTONUP,
              MOUSEBUTTONDOWN,
              MOUSEMOTION,

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

### define scrolling speeds in different 2D axes

X_SCROLLING_SPEED = 20
Y_SCROLLING_SPEED = 20

### obtain fps maintaining operation
maintain_fps = Clock().tick


class ImageViewer:
    """Manages the loop of the split_view() node."""

    def __init__(self):

        ### create a scroll area so the image can be moved
        ### around
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

        ### instantiate background

        self.background = (
          Surface(SCREEN.get_size()).convert()
        )

        ### create flag so drawing the checker pattern can
        ### be postponed to when the node is executed
        self.must_draw_checker_pattern = True

    def keyboard_mode_event_handling(self):

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.enable_mouse_mode()

            elif event.type == KEYUP:

                if event.key == K_HOME:

                    self.image_rect.center = (
                      SCREEN_RECT.center
                    )

                elif event.key == K_ESCAPE:
                    self.running = False

    def keyboard_mode_key_state_handling(self):
        """Handle the state of keys."""

        key_input = get_pressed_keys()

        ### calculate x movement

        if self.moves_horizontally:

            go_left = any(
              key_input[key] for key in (K_a, K_LEFT)
            )

            go_right = any(
              key_input[key] for key in (K_d, K_RIGHT)
            )

            if go_left and not go_right:
                dx = -1 * X_SCROLLING_SPEED

            elif go_right and not go_left:
                dx = 1 * X_SCROLLING_SPEED

            else: dx = 0

        else: dx = 0

        ### calculate y movement

        if self.moves_vertically:

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
                dy = 0

            elif go_up and not go_down:
                dy = -1 * Y_SCROLLING_SPEED

            elif go_down and not go_up:
                dy = 1 * Y_SCROLLING_SPEED

        else: dy = 0

        ### apply movement if a delta is found
        if dx or dy: self.move_image(dx, dy)

    def move_image(self, dx, dy):

        image_rect  = self.image_rect
        scroll_area = self.scroll_area

        ### apply x movement if != 0

        if dx < 0:

            if (
              (image_rect.right + dx)
              < scroll_area.right
            ):
                image_rect.right = scroll_area.right

            else: image_rect.x += dx

        elif dx > 0:

            if (
              (image_rect.left + dx)
              > scroll_area.left
            ):
                image_rect.left = scroll_area.left

            else: image_rect.x += dx

        ### apply y movement if != 0

        if dy < 0:

            if (
              (image_rect.bottom + dy)
              < scroll_area.bottom
            ):
                image_rect.bottom = scroll_area.bottom

            else: image_rect.y += dy

        elif dy > 0:

            if (
              (image_rect.top + dy)
              > scroll_area.top
            ):
                image_rect.top = scroll_area.top

            else: image_rect.y += dy

    def mouse_mode_event_handling(self):

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == MOUSEMOTION:
                self.move_according_to_mouse(*event.rel)

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:
                    self.enable_keyboard_mode()

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.running = False

    def move_according_to_mouse(self, dx, dy):

        if not self.moves_horizontally:
            dx = 0

        if not self.moves_vertically:
            dy = 0

        self.move_image(dx, dy)

    def mouse_mode_key_state_handling(self):
        """Do nothing."""

    def watch_window_size(self):
        """Watch out for window resizing.

        And perform needed setups when it is the case
        """

        ### if the screen and the background have the
        ### same size, then no window resizing took place,
        ### so we exit the function right away

        if SCREEN.get_size() == self.background.get_size():
            return

        ### other, we keep executing the function,
        ### performing the window resize setups

        ## reference image surf and rect locally

        image_surf = self.image_surf
        image_rect = self.image_rect

        ## update the screen rect's size
        SCREEN_RECT.size = SCREEN.get_size()

        ## center the image on the screen
        image_rect.center = SCREEN_RECT.center

        ## update the moving flags

        self.moves_horizontally = (
          image_rect.width > SCREEN_RECT.width
        )

        self.moves_vertically = (
          image_rect.height > SCREEN_RECT.height
        )

        ## recreate the background

        self.background = (

          Surface(SCREEN.get_size()).convert()

        )

        ## redraw the checker pattern on the background
        blit_checker_pattern(self.background)

        ## clean the screen
        SCREEN.blit(self.background, (0, 0))

        ## blit image on the screen using its rect
        SCREEN.blit(image_surf, image_rect)

        ## replace the scroll area
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

    def split_view(

          self,

          image1: Image,
          image2: Image,

          axis_to_split: {
            'widget_name': 'option_tray',
            'widget_kwargs': {
              'options': ['X', 'Y'],
            },
            'type': str,
          } = 'X',

          factor: {

            'widget_name': 'int_float_entry',
            'widget_kwargs': {
              'min_value': 0,
              'max_value': 100,
            },
            'type': int,

          } = 50,

        ):
        """Display image centered on screen.

        To stop displaying the image just press <Escape>.
        This will trigger the exit of the inner loop.
        """
        ### enable keyboard mode
        self.enable_keyboard_mode()

        ### draw the checker pattern on the background if
        ### needed

        if self.must_draw_checker_pattern:

            ### draw the checker pattern on the background
            blit_checker_pattern(self.background)

            ### set flag to false
            self.must_draw_checker_pattern = False

        ### obtain surfaces from pillow images

        surf1 = surf_from_pillow_image(image1)
        surf2 = surf_from_pillow_image(image2)

        surf = Surface(image1.size).convert()
        rect = surf.get_rect()

        if axis_to_split.lower() == 'y':
            rect.size = (*reversed(rect.size),)

        factor1 = factor / 100
        factor2 = 1.0 - factor1

        rect1 = rect.copy()
        rect2 = rect.copy()

        rect1.w *= factor1
        rect2.w *= factor2

        if axis_to_split.lower() == 'y':
            
            for r in (rect, rect1, rect2):
                r.size = (*reversed(r.size),)

            rect2.topleft = rect1.bottomleft

        else: rect2.topleft = rect1.topright


        surf.blit(surf1.subsurface(rect1), rect1)
        surf.blit(surf2.subsurface(rect2), rect2)

        ### clean the screen
        SCREEN.blit(self.background, (0, 0))

        ### get rect for image and center it on the screen

        rect = surf.get_rect()

        rect.center = SCREEN_RECT.center

        ### update the moving flags

        self.moves_horizontally = (
          rect.width > SCREEN_RECT.width
        )

        self.moves_vertically = (
          rect.height > SCREEN_RECT.height
        )

        ### store image surface and rect

        self.image_surf = surf
        self.image_rect = rect

        ### blit image on the screen using its rect
        SCREEN.blit(surf, rect)

        ### create attribute to track topleft position
        self.last_topleft = rect.topleft

        ### loop
        self.loop()

        ### remove image surf and rect references

        del self.image_surf
        del self.image_rect

    ### set special attribute on split_view method
    split_view.dismiss_exec_time_tracking = True

    def loop(self):

        self.running = True

        while self.running:

            maintain_fps(30)

            self.watch_window_size()

            self.handle_events()
            self.handle_key_state()
            self.draw()

            ### update screen (pygame.display.update())
            update()

    def enable_keyboard_mode(self):
        """Set behaviour to move image with keyboard."""

        self.handle_events = (
          self.keyboard_mode_event_handling
        )

        self.handle_key_state = (
          self.keyboard_mode_key_state_handling
        )

    def enable_mouse_mode(self):
        """Set behaviour to move image with the mouse.

        That is, by dragging.
        """

        self.handle_events = (
          self.mouse_mode_event_handling
        )

        self.handle_key_state = (
          self.mouse_mode_key_state_handling
        )

    def draw(self):
        """If image moved, redraw."""

        ### if the image is in the same position,
        ### do nothing by returning early

        if (
          self.last_topleft == self.image_rect.topleft
        ): return

        ### otherwise store the current position and
        ### redraw background and image

        self.last_topleft = self.image_rect.topleft

        SCREEN.blit(self.background, (0, 0))

        SCREEN.blit(
                 self.image_surf, self.image_rect
               )


### finally, we just need to instantiate the ImageViewer
### and use the split_view method as the main callable;
###
### note that we also make it so the callable can be found in
### this module using its own name, that is, 'split_view';
###
### we do so because when the node layout is exported as a python
### script, its name is used to find the callable
main_callable = split_view = ImageViewer().split_view


### utility functions

def surf_from_pillow_image(image):

    mode = image.mode
    size = image.size
    data = image.tobytes()

    return image_from_string(data, size, mode)

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
