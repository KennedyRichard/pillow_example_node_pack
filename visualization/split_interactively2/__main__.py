"""Facility for image visualization."""

### standard library import
from itertools import cycle


### third-party imports

## pygame-ce

from pygame import (

  QUIT, KEYUP, K_ESCAPE,

  MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,

  K_w, K_a, K_s, K_d,
  K_UP, K_LEFT, K_DOWN, K_RIGHT,
  K_HOME,

  Surface, Rect,

)

from pygame.math import Vector2

from pygame.display import get_surface, update
from pygame.time    import Clock
from pygame.event   import get as get_events
from pygame.image   import fromstring as image_from_string

from pygame.mouse import (
    get_pos as get_mouse_pos,
    set_pos as set_mouse_pos,
)

from pygame.transform import (
    rotate as rotate_surface,
    smoothscale as smoothscale_surface
)

from pygame.draw import (
    rect   as draw_rect,
    line   as draw_line,
    lines  as draw_lines,
    circle as draw_circle,
)

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


## 2D vector representing origin
ORIGIN = Vector2()



class ImageViewer:
    """Manages the loop of the split_interactively2() node."""

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

        ### create a rect for the widget
        self.widget_rect = X_SPLIT_SURF.get_rect()

    def keyboard_mode_event_handling(self):

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:
                
                    if (

                      self
                      .widget_rect
                      .collidepoint(event.pos)

                    ):

                        set_mouse_pos(
                          self.widget_rect.center
                        )

                        self.last_widget_center = (
                          self.widget_rect.center
                        )

                        self.enable_widget_drag_mode()

                    else: self.enable_mouse_mode()

            elif event.type == KEYUP:

                if event.key == K_HOME:

                    self.split_rect.center = (
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

        image_rect  = self.split_rect
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

    def widget_drag_mode_event_handling(self):

        for event in get_events():

            if event.type == QUIT:
                self.running = False

            elif event.type == MOUSEBUTTONUP:

                if event.button == 1:

                    self.perform_split()
                    self.enable_keyboard_mode()

            elif event.type == KEYUP:

                if event.key == K_ESCAPE:
                    self.running = False

    def split_on_x(self):

        surf = self.split_surf
        rect = self.split_rect

        rect1 = rect.copy()
        rect2 = rect.copy()

        rect1.w = self.widget_rect.centerx - rect.x
        rect2.w = rect.w - rect1.w

        rect2.topleft = rect1.topright

        offset = -Vector2(rect.topleft)

        offset_rect1 = rect1.move(offset)
        offset_rect2 = rect2.move(offset)

        rect1_subsurf = self.surf1.subsurface(offset_rect1)
        rect2_subsurf = self.surf2.subsurface(offset_rect2)

        surf.blit(rect1_subsurf, offset_rect1)
        surf.blit(rect2_subsurf, offset_rect2)

        self.draw_surfaces()

    def split_on_y(self):

        surf = self.split_surf
        rect = self.split_rect

        rect1 = rect.copy()
        rect2 = rect.copy()

        rect1.h = self.widget_rect.centery - rect.y
        rect2.h = rect.h - rect1.h

        rect2.topleft = rect1.bottomleft

        offset = -Vector2(rect.topleft)

        offset_rect1 = rect1.move(offset)
        offset_rect2 = rect2.move(offset)

        rect1_subsurf = self.surf1.subsurface(offset_rect1)
        rect2_subsurf = self.surf2.subsurface(offset_rect2)

        surf.blit(rect1_subsurf, offset_rect1)
        surf.blit(rect2_subsurf, offset_rect2)

        self.draw_surfaces()

    def widget_drag_mode_key_state_handling(self):
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

    def widget_drag_mode_update(self):

        mouse_pos = get_mouse_pos()

        self.widget_rect.center = mouse_pos

        self.widget_rect.clamp_ip(self.split_rect)

    def widget_drag_mode_draw(self):
        """If image or widget moved, redraw."""

        ### check whether the image and the widget moved

        image_moved = (
          self.image_topleft != self.split_rect.topleft
        )

        mouse_pos = get_mouse_pos()

        widget_moved = (

          self.last_widget_center
          != self.widget_rect.center

        )

        ### if neither moved, exit the method earlier by
        ### returning
        if not image_moved and not widget_moved: return

        ### otherwise store the new positions and
        ### redraw elements

        if image_moved:
            self.image_topleft = self.split_rect.topleft

        if widget_moved:

            self.last_widget_center = (
              self.widget_rect.center
            )

        SCREEN.blit(self.background, (0, 0))

        SCREEN.blit(
                 self.split_surf, self.split_rect
               )

        self.draw_split_axis()

        SCREEN.blit(
                 self.widget_surf, self.widget_rect
               )

    def draw_x_axis(self):

        image_rect  = self.split_rect
        widget_rect = self.widget_rect

        start = image_rect.left,  widget_rect.centery
        end   = image_rect.right, widget_rect.centery

        draw_line(
          SCREEN,
          (255, 255, 0),
          start,
          end,
          3,
        )

    def draw_y_axis(self):

        image_rect  = self.split_rect
        widget_rect = self.widget_rect

        start = widget_rect.centerx, image_rect.top
        end   = widget_rect.centerx, image_rect.bottom

        draw_line(
          SCREEN,
          (255, 255, 0),
          start,
          end,
          3,
        )

    def watch_window_size(self):
        """Watch out for window resizing.

        And perform needed setups when it is the case
        """

        ### if the screen and the background have the
        ### same size, then no window resizing took place,
        ### so we exit the function right away

        if SCREEN.get_size() == self.background.get_size():
            return

        ### otherwise, we keep executing the function,
        ### performing the window resize setups

        ## reference image surf and rect locally

        image_surf = self.split_surf
        image_rect = self.split_rect

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

        ##
        self.draw_surfaces()

        ## replace the scroll area
        self.scroll_area = SCREEN_RECT.inflate(-80, -80)

    def loop(self):

        self.running = True

        while self.running:

            maintain_fps(30)

            self.watch_window_size()

            self.handle_events()
            self.handle_key_state()
            self.update()
            self.draw()

            ### update screen (pygame.display.update())
            update()

        ### XXX after leaving the loop, we could clear unneeded
        ### references

    def enable_keyboard_mode(self):
        """Set behaviour to move image with keyboard."""

        self.handle_events = (
          self.keyboard_mode_event_handling
        )

        self.handle_key_state = (
          self.keyboard_mode_key_state_handling
        )

        self.update = empty_function

        self.draw = self.draw_when_image_moves

    def enable_mouse_mode(self):
        """Set behaviour to move image with the mouse.

        That is, by dragging.
        """

        self.handle_events = (
          self.mouse_mode_event_handling
        )

        self.handle_key_state = empty_function

        self.update = empty_function

        self.draw = self.draw_when_image_moves

    def enable_widget_drag_mode(self):
        """Set behaviour to split image by dragging widget.

        After having clicked on it.
        """
        self.handle_events = (
          self.widget_drag_mode_event_handling
        )

        self.handle_key_state = (
          self.widget_drag_mode_key_state_handling
        )

        self.update = self.widget_drag_mode_update

        self.draw = self.widget_drag_mode_draw

    def draw_when_image_moves(self):
        """If image moved, redraw."""

        ### if the image is in the same position,
        ### do nothing by returning early

        if (
          self.image_topleft == self.split_rect.topleft
        ): return

        ### otherwise store the current position and
        ### redraw background and image

        diff = (
          Vector2(self.split_rect.topleft)
          - self.image_topleft
        )

        self.image_topleft = self.split_rect.topleft

        self.widget_rect.move_ip(diff)

        self.draw_surfaces()

    keyboard_mode_draw = mouse_mode_draw = (
      draw_when_image_moves
    )

    def draw_surfaces(self):

        SCREEN.blit(self.background, (0, 0))

        SCREEN.blit(
                 self.split_surf, self.split_rect
               )

        SCREEN.blit(self.widget_surf, self.widget_rect)

    def split_interactively2(

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

          max_preview_size : 'natural_number' = 600,


        ):
        """Display image as result of parts of 02 images.

        Inside the inner loop, the user can change the point
        at which the image is split interactively.

        To stop displaying the image just press <Escape>.
        This will trigger the exit of the inner loop.

        Parameters
        ==========
        image1, image2
            Instances of PIL.Image.Image used to form a single one.
        axis_to_split
            Axis in which to split the images to assemble the
            parts together. Must be either 'X' or 'Y', case-insensitive.
        max_preview_size
            Maximum diagonal length of the preview surface. Must be >= 0.
            If 0, just use the full surface.
        """
        loop_data = (
            get_processed_image_data(
                image1,
                image2,
                axis_to_split,
                max_preview_size,
            )
        )['loop_data']

        self.display_split_image(loop_data)

    def display_split_image(self, data):

        axis_to_split = data['axis_to_split']
        surf1 = data['surf1']
        surf2 = data['surf2']
        split_surf = data['split_surf']
        split_rect = data['split_rect']

        ### enable keyboard mode
        self.enable_keyboard_mode()

        ### draw the checker pattern on the background if
        ### needed

        if self.must_draw_checker_pattern:

            ### draw the checker pattern on the background
            blit_checker_pattern(self.background)

            ### set flag to false
            self.must_draw_checker_pattern = False


        ### set split widget surf and center it
        self.perform_axis_setups(axis_to_split)

        ### obtain surfaces from pillow images

        self.surf1 = surf1
        self.surf2 = surf2

        self.split_surf = split_surf
        self.split_rect = split_rect

        self.split_rect.center  = SCREEN_RECT.center
        self.widget_rect.center = SCREEN_RECT.center

        self.perform_split()

        ### update the moving flags

        self.moves_horizontally = (
          self.split_rect.width > SCREEN_RECT.width
        )

        self.moves_vertically = (
          self.split_rect.height > SCREEN_RECT.height
        )

        ### create attribute to track topleft position
        self.image_topleft = self.split_rect.topleft

        ### loop
        self.loop()

    ### set special attribute on split_interactively2
    ### method
    split_interactively2.dismiss_exec_time_tracking = True

    def perform_axis_setups(self, axis_to_split):

        axis_to_split = axis_to_split.lower()

        if axis_to_split == 'x':

            self.draw_split_axis = self.draw_y_axis
            self.perform_split   = self.split_on_x

            self.widget_surf = X_SPLIT_SURF

        elif axis_to_split == 'y':

            self.draw_split_axis = self.draw_x_axis
            self.perform_split   = self.split_on_y

            self.widget_surf = Y_SPLIT_SURF

        else:

            raise ValueError(
                    "Axis to split must be 'x' or 'y'."
                  )


### finally, we just need to instantiate the ImageViewer
### and reference/alias/define the relevant operations

## instantiate
image_viewer = ImageViewer()

## use the view_figure method as the main callable;
##
## note that we also make it so the callable can be found in
## this module using its own name, that is, 'view_figure';
##
## we do so because when the node layout is exported as a python
## script, its name is used to find the callable
main_callable = split_interactively2 = image_viewer.split_interactively2

## alias the display_split_image method as the function to enter the
## viewer loop
enter_viewer_loop = image_viewer.display_split_image

## define a function to process and return data related to visuals
## (side visual data and loop visual data) and output of the main callable;
##
## it must:
##
## - have a signature compatible with the signature of the main callable;
## - be called or aliased loopviz_sideviz_and_output_backdoor;
## - return a dict with specific keys, as described in its docstring.

def get_processed_image_data(
    image1: Image,
    image2: Image,
    axis_to_split:str='X',
    max_preview_size: 'natural_number' = 600,
):
    """Return dict with data representing visuals and outputs.

    The 'in_graph_visual' key must contain data representing a preview
    of the visualization within the viewer loop. Though it represents
    a preview, it can be the whole visual if you desire. It is expected
    to be a pygame.Surface object, but more data might be accepted in
    the future to provide more advanced previews.

    The 'loop_data' item contains data to be delivered to the function used
    to enter the viewer loop. This function uses such data to update
    its inner visualization machinery
    """
    ### raise error if value of max preview size is not allowed

    if max_preview_size < 0:
        raise ValueError("'max_preview_size' must be >= 0")

    ### obtain surfaces from pillow images

    surf1 = surf_from_pillow_image(image1)
    surf2 = surf_from_pillow_image(image2)

    split_surf = Surface(surf1.get_size()).convert()
    rect = split_surf.get_rect()

    rect1 = rect.copy()
    rect2 = rect.copy()

    if axis_to_split.lower() == 'x':

        rect1.w = rect.centerx - rect.x
        rect2.w = rect.right - rect.centerx

        rect2.topleft = rect1.topright

    elif axis_to_split.lower() == 'y':

        rect1.h = rect.centery - rect.y
        rect2.h = rect.bottom - rect.centery

        rect2.topleft = rect1.bottomleft

    ##
    rect1_subsurf = surf1.subsurface(rect1)
    rect2_subsurf = surf2.subsurface(rect2)

    ##
    split_surf.blit(rect1_subsurf, rect1)
    split_surf.blit(rect2_subsurf, rect2)

    ### the split_surf is our full surface
    full_surface = split_surf

    ### if the max preview size is 0, it means the preview doesn't need
    ### to be below a specific size, so we can use the full surface
    ### as the preview

    if not max_preview_size:

        preview_surface = full_surface

        return {
            'in_graph_visual': preview_surface,
            'loop_data': {
                'axis_to_split': axis_to_split,
                'surf1': surf1,
                'surf2': surf2,
                'split_surf': split_surf,
                'split_rect': rect,
            },
        }

    ### otherwise, we must create a preview surface within the allowed size,
    ### if the full surface surpasses such allowed size

    ## obtain the bottom right coordinate of the surface, which is
    ## equivalent to its size
    bottomright = full_surface.get_size()

    ## use the bottom right to calculate its diagonal length
    diagonal_length = ORIGIN.distance_to(bottomright)

    ## if the diagonal length of the full surface is higher than the
    ## maximum allowed size, we create a new smaller surface within
    ## the allowed size to use as the preview

    if diagonal_length > max_preview_size:

        size_proportion = max_preview_size / diagonal_length
        new_size = ORIGIN.lerp(bottomright, size_proportion)

        preview_surface = smoothscale_surface(full_surface, new_size)


    ### otherwise, just alias the full surface as the preview surface;
    ###
    ### that is, since the full surface didn't need to be downscaled,
    ### it means it is small enough to be used as an in-graph visual
    ### already

    else:
        preview_surface = full_surface


    ### return data

    return {
        'in_graph_visual': preview_surface,
        'loop_data': {
            'axis_to_split': axis_to_split,
            'surf1': surf1,
            'surf2': surf2,
            'split_surf': split_surf,
            'split_rect': rect,
        },
    }

loopviz_sideviz_and_output_backdoor = get_processed_image_data



### utility functions

def empty_function():
    """Does nothing"""

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
