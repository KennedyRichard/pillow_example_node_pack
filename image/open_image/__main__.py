
### standard library import
from pathlib import Path


### third-party imports

from PIL.Image import (
                 Image,
                 open as pil_open_image,
               )


### get the path for a dummy image

current_file_path = Path(__file__)

dummy_image_path = \
  current_file_path.parent / 'full_saturation_spectrum.png'

image_str_path = str(dummy_image_path)


### function definition

def open_image(

      filepath : {
        'widget_name': 'image_preview',
        'type' : str
      } = image_str_path,

    ) -> [

      {'name' : 'image',  'type': Image},
      {'name' : 'width',  'type': int},
      {'name' : 'height', 'type': int},
      {'name' : 'size',   'type': tuple},
      {'name' : 'mode',   'type': str},

    ]:
    """Return PIL.Image.Image obj copy from filepath.

    Parameters
    ==========

    filepath (string, pathlib.Path or a file object)
        path to image file. If a file object is given
        it must implement read(), seek(), and tell()
        methods, and be opened in binary mode.

    Returns
    =======
    An Image object.

    Raises
    ======
    IOError – if the file cannot be found, or the image
    cannot be opened and identified.

    Warning
    =======

    To protect against potential DOS attacks caused by
    "decompression bombs" (i.e. malicious files which
    decompress into a huge amount of data and are designed
    to crash or cause disruption by using up a lot of
    memory), Pillow will issue a DecompressionBombWarning
    if the image is over a certain limit. If desired, the
    warning can be turned into an error with

    warnings.simplefilter(
    'error', Image.DecompressionBombWarning) or
    suppressed entirely with
    warnings.simplefilter(
    'ignore', Image.DecompressionBombWarning).
    
    See also the logging documentation to have warnings
    output to the logging facility instead of stderr.
    """
    ### retrieve a copy of the image, so the file can
    ### be closed

    # pil_open_image = PIL.Image.open

    with pil_open_image(filepath, 'r') as temp_image:
        image = temp_image.copy()

    ### return the copy along with its data

    return {
      'image'  : image,
      'width'  : image.width,
      'height' : image.height,
      'size'   : image.size,
      'mode'   : image.mode,
    }

### function aliasing
main_callable = open_image
