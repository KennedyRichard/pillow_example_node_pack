
from PIL.Image import Image

def save_image(

      image  : Image,
      path   : 'image_path' = '.',
      format : 'python_literal' = None,

    ):

    image.save(path, format=format)

main_callable = save_image
