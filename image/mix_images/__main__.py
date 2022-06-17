
### third-party imports

from PIL.Image import Image

from PIL.ImageChops import (
                      add,
                      darker,
                      difference,
                      lighter,
                      multiply,
                      soft_light,
                      hard_light,
                      overlay,
                      screen,
                      subtract,
                    )


BLEND_OPERATION_MAP = {
  'add'             : add,
  'darker'          : darker,
  'difference'      : difference,
  'lighter'         : lighter,
  'multiply'        : multiply,
  'soft_light'      : soft_light,
  'hard_light'      : hard_light,
  'overlay'         : overlay,
  'screen'          : screen,
  'subtract'        : subtract,
}


def mix_images(
      
      image1: Image,

      image2: Image,
      
      operation_name : {
        'widget_name': 'option_menu',
        'widget_kwargs': {
          'options': tuple(BLEND_OPERATION_MAP),
        },
        'type': str,
      } = 'multiply',

    ) -> [
      {'name': 'image', 'type': Image},
    ]:
    """"""
    operation = BLEND_OPERATION_MAP[operation_name]
    return operation(image1, image2)

main_callable = mix_images
