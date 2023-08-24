"""Facility for image visualization."""

### third-party imports

## pygame-ce

from pygame import Surface

from pygame.math import Vector2

from pygame.image import frombytes as image_from_bytes

from pygame.transform import smoothscale as smoothscale_surface



## Pillow
from PIL.Image import Image




### 2D vector representing origin
ORIGIN = Vector2()


### main callable

def split_view2(

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

      max_preview_size : 'natural_number' = 600,

) -> [

    {'name': 'full_surface', 'type': Surface, 'viz': 'loop'},
    {'name': 'preview_surface', 'type': Surface, 'viz': 'side'},

]:
    """Return dict with surfaces representing combined Pillow images.

    Parameters
    ==========
    image1, image2
        Instances of PIL.Image.Image used to form a single one.
    axis_to_split
        Axis in which to split the images to assemble the
        parts together must be either 'X' or 'Y', case-insensitive
    factor
        Percentage of image where the split should appear.
    max_preview_size
        Maximum diagonal length of the preview surface. Must be >= 0.
        If 0, just use the full surface.
    """
    ### raise error if value of max preview size is not allowed

    if max_preview_size < 0:
        raise ValueError("'max_preview_size' must be >= 0")

    ### obtain surfaces from pillow images

    surf1 = surf_from_pillow_image(image1)
    surf2 = surf_from_pillow_image(image2)

    ### create new surface with surfaces drawn on it

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

    ### surf is our full surface
    full_surface = surf

    ### if the max preview size is 0, it means the preview doesn't need
    ### to be below a specific size, so we can use the full surface
    ### as the preview

    if not max_preview_size:

        preview_surface = full_surface

        return {
            'full_surface': full_surface,
            'preview_surface': preview_surface,
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

    ### finally, return a dict containing both surfaces;
    ###
    ### you can return the surfaces in any way you want, inside a list,
    ### inside a tuple or a dictionary, etc.; the format isn't important,
    ### because we specify functions further below in the script to fetch
    ### them for us regardless of where we placed them anyway

    return {
        'full_surface': full_surface,
        'preview_surface': preview_surface,
    }



### alias split_view2 as main_callable
main_callable = split_view2




### utility function

def surf_from_pillow_image(image):

    mode = image.mode
    size = image.size
    data = image.tobytes()

    return image_from_bytes(data, size, mode)
