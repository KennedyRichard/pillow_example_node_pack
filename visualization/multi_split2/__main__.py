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

def multi_split_view2(

      *images: Image,

      axis_to_split: {
        'widget_name': 'option_tray',
        'widget_kwargs': {
          'options': ['X', 'Y'],
        },
        'type': str,
      } = 'X',

      max_preview_size: 'natural_number' = 600,

) -> [

    {'name': 'full_surface', 'type': Surface, 'viz': 'loop'},
    {'name': 'preview_surface', 'type': Surface, 'viz': 'side'},

]:
    """Return dict with surfaces representing combined Pillow images.

    Parameters
    ==========
    *images
        Instances of PIL.Image.Image used to form a single one.
    axis_to_split
        Axis in which to split the images to assemble the
        parts together must be either 'X' or 'Y', case-insensitive
    max_preview_size
        Maximum diagonal length of the preview surface. Must be >= 0.
        If 0, just use the full surface.
    """

    ### raise errors if no images are given

    if len(images) < 2:
        raise ValueError("'images' must contain at least 02 images")

    if any(
        not isinstance(img, Image)
        for img in images
    ):

        raise TypeError(
                "All given images must be Pillow images (PIL.Image.Image)."
              )

    ### raise error if value of max preview size is not allowed

    if max_preview_size < 0:
        raise ValueError("'max_preview_size' must be >= 0")


    ### obtain surfaces from pillow images

    surfs = [
      surf_from_pillow_image(image)
      for image in images
    ]

    ### create surface containing multiple areas in it, one
    ### for each given surface

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

    ## the canvas we used to blit the subsurfaces is our full surface
    full_surface = canvas

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


### alias multi_split_view2 as the main_callable
main_callable = multi_split_view2



### utility function

def surf_from_pillow_image(image):

    mode = image.mode
    size = image.size
    data = image.tobytes()

    return image_from_bytes(data, size, mode)

