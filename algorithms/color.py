"""
algorithm refactored from CairX/extract-colors-py by Thomas Cairns
"""
import collections
import math
from convcolors import rgb_to_lab


class Color:
    def __init__(self,rgb=None, lab=None, name=None, count=0):
        self.rgb = rgb
        self.name = name
        self.lab = lab
        self.count = count
        self.pixelpct = None

    def __lt__(self, other):
        return self.count < other.count


def diff_cie76(c1, c2):
    """
    Color comparision using CIE76 algorithm.
    Returns a float value where 0 is a perfect match and 100 is
    opposing colors. Note that the range can be larger than 100.
    http://zschuessler.github.io/DeltaE/learn/

    LAB Delta E - version CIE76
    https://en.wikipedia.org/wiki/Color_difference

    E* = 2.3 corresponds to a JND (just noticeable difference)
    """
    l = c2[0] - c1[0]
    a = c2[1] - c1[1]
    b = c2[2] - c1[2]
    return math.sqrt((l * l) + (a * a) + (b * b))


def main_color(rgbs, names):
    """ Generating main color objects
        :return: main_colors
    """
    main_colors = []
    for rgb, name in zip(rgbs, names):
        lab = rgb_to_lab(rgb)
        main_colors.append(Color(rgb=rgb, lab=lab, name=name))
    return main_colors


def main_color_init(main_colors):
    """ Set color pixels count to 0 when analyzing a new image
        :return: None
    """
    for color in main_colors:
        color.count = 0


def extract_from_pixels(pixels, main_colors):
    """ Calculate color percentages from image
        :return: colors
    """
    pixels = _filter_fully_transparent(pixels)
    pixels = _strip_alpha(pixels)
    colors = _count_colors(pixels)
    colors = colors_to_main(colors, main_colors)
    for color in colors:
        color.pixelpct = color.count / len(pixels)
    return colors


def _filter_fully_transparent(pixels):
    return [p for p in pixels if p[3] > 0]


def _strip_alpha(pixels):
    return [(p[0], p[1], p[2]) for p in pixels]


def _count_colors(pixels):
    """ Count pixels for each color in the image
        :return: colors
    """
    counter = collections.defaultdict(int)
    for color in pixels:
        counter[color] += 1

    colors = []
    for rgb, count in counter.items():
        lab = rgb_to_lab(rgb)
        colors.append(Color(rgb=rgb, lab=lab, count=count))

    return colors


def lab_to_color(lab):
    """ Mapping lab to white and black colors
        (white, silver, gray, black)
        https://en.wikipedia.org/wiki/CIELAB_color_space
        :param: lab: color in CIELAB color space
        :return: None
    """
    if -5 <= lab[1] <= 5 and -5 <= lab[2] <= 5:
        if lab[0] < 15:
            return 'black'
        elif lab[0] < 40:
            return 'gray'
        elif lab[0] < 85:
            return 'silver'
        return 'white'
    else:
        return None


def colors_to_main(colors, main_colors):
    """ Mapping image colors to main colors and count pixels
        :param: colors: all colors in image
        :param: main_colors: input main colors
        (blue, green, yellow, purple, pink, red, orange, brown, silver, white, gray, black)
        :return: colors
    """
    colors.sort(reverse=True)
    main_color_init(main_colors)
    for c1 in colors:
        color_flag = lab_to_color(c1.lab)

        smallest_diff = 1000
        smallest_index = None

        for n, c2 in enumerate(main_colors):
            if color_flag is not None:
                if c2.name == color_flag:
                    smallest_index = n
                    break
            else:
                if c2.name in ['white', 'silver', 'gray', 'black']:
                    continue
                color_diff = diff_cie76(c1.lab, c2.lab)
                if color_diff < smallest_diff:
                    smallest_diff = color_diff
                    smallest_index = n
        main_colors[smallest_index].count += c1.count
    colors = [color for color in main_colors]
    colors.sort(reverse=True)
    return colors


