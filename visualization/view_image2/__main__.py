
### third-party imports

## pygame-ce

from pygame import Surface

from pygame.math import Vector2

from pygame.image import fromstring as image_from_string

from pygame.transform import smoothscale as smoothscale_surface


## Pillow
from PIL.Image import Image



### 2D vector representing origin
ORIGIN = Vector2()


### main callable

def view_image2(

    image: Image,
    max_preview_size: 'natural_number' = 600,

) -> [

    {'name': 'full_surface', 'type': Surface, 'viz': 'loop'},
    {'name': 'preview_surface', 'type': Surface, 'viz': 'side'},

]:
    """Return dict with pygame-ce surfaces representing given image.

    Parameters
    ==========
    image
        Pillow image from which to create surfaces.
    max_preview_size
        maximum diagonal length of the preview surface. Must be >= 0.
        If 0, just use the full surface.
    """

    ### raise error if value of max preview size is not allowed

    if max_preview_size < 0:
        raise ValueError("'max_preview_size' must be >= 0")

    ### obtain surface from pillow image

    mode = image.mode
    size = image.size
    data = image.tobytes()

    full_surface = image_from_string(data, size, mode)

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


### alias the function defining the node as main_callable
main_callable = view_image2
