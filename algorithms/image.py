"""
algorithm refactored from CairX/extract-colors-py by Thomas Cairns
"""
import os
import algorithms.color as extcolor
from PIL import Image
import imageio
import numpy as np
import base64
import io
import time

execution_path = os.path.join(os.getcwd(), 'algorithms/')


def timeit(func):
    """ Decorator for measuring function's running time.
        from stackoverflow answer by Vinh Khuc
    """

    def measure_time(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        print("Processing time of %s(): %.10f seconds."
              % (func.__qualname__, time.time() - start_time))
        return result

    return measure_time


class Img:
    """ Image class
        With input image, calculate main color percentage.
    """

    def __init__(self, string=None, img=None, filename=None):
        """ Constructor to setup ann image.
            :param string: image string encoded in base64
            :param img: a PIL image
            :param filename: image filename for loading local image
        """
        self.filename = filename
        self.img = img
        self.colors = None
        self.string = string
        self.pixels = None
        self.count = None
        if self.filename is not None:
            self.filepath = os.path.join(execution_path, self.filename)
            self.img = Image.open(self.filepath)

    def b64_to_pil(self):
        """ Converting b64 image to PIL image.
            :return: None
        """
        decoded = base64.b64decode(self.string)
        buffer = io.BytesIO(decoded)
        self.img = Image.open(buffer)

    # def get_dimension(self):
    #     height, width = self.img.size
    #     return width, height

    @timeit
    def getcolor(self, main_colors):
        """ Get and return image color percentages.
            :param: main_colors: colors to calculate percentages for
            :return: img_colors: list of color name and percentage
        """
        width, height = self.img.size
        ratio = height / width
        if width > 500:
            newsize = (500, int(500 * ratio))
            self.img = self.img.resize(newsize)
        elif height > 500:
            newsize = (int(500 / ratio), 500)
            self.img = self.img.resize(newsize)
        self.pixels = list(self.img.convert("RGBA").getdata())
        self.count = len(self.pixels)
        colors = extcolor.extract_from_pixels(self.pixels, main_colors=main_colors)
        self.colors = colors
        img_colors = [(color.name, color.count / self.count) for color in colors]
        return img_colors

    def save_palette(self):
        """ Save the image's main color palette to jpg file
            :return: None
        """
        limit_colors = [_ for _ in self.colors if _.pixelpct >= 0.001]
        im = np.array([[color.rgb for color in limit_colors]], dtype=np.uint8)
        bigger_img = im.repeat(100, axis=0).repeat(100, axis=1)
        imageio.imwrite(os.path.join(execution_path, self.filename.strip('.jpg') + '_palette.jpg'), bigger_img)

    def __str__(self):
        """ Nicely print color name, rgb, and percentage
            :return: print text
        """
        text = '\nExtracted colors:\n'
        for color in self.colors:
            text += f'{str(color.name)}: {str(color.rgb)} {color.pixelpct * 100:.2f}%\n'
        return text
