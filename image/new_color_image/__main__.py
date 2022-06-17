
from PIL.Image import (
                 Image,
                 new as new_image,
               )

def new_color_image(

      size: tuple,

      color : {
        'widget_name': 'color_button',
        'type': tuple,
      } = (255, 0, 0),

    ) -> [

      {'name': 'image', 'type': Image},
      {'name': 'mode', 'type': str},

    ]:
    """Creates a new image with the given size and color.

    The mode will be either RGB or RGBA, depending on
    whether the color has alpha or not.

    Parameters
    ==========

    size (2-tuple of integers)
        integers represent size (width and height) in pixels
    color (int, float, tuple, None)
        color to use for the image. Default is black. If
        given, this should be a single integer or floating
        point value for single-band modes, and a tuple for
        multi-band modes (one value per band). When creating
        RGB images, you can also use color strings as
        supported by the ImageColor module. If the color
        is None, the image is not initialised.
    """
    mode = 'RGBA' if len(color) == 4 else 'RGB'

    # new_image = PIL.Image.new

    image = new_image(
              mode,
              size,
              color
            )

    return {
      'image' : image,
      'mode'  : mode,
    }

main_callable = new_color_image
