import pytest
import pandas as pd

from algorithms.image import *
from algorithms.color import *
from app import get_quotes_pool, get_n_quotes

import os

## Data preparation
#
cwd = os.getcwd()
df_color = pd.read_csv(os.path.join(cwd,'data/color_tag.csv'))

def int_str_to_lst(value):
    return list(value.strip('[]').split(', '))

def str_to_lst(value):
    return list(value.strip('[]').strip("''").split("', '"))

color_dict = {}
for t in df_color.itertuples():
    color_dict[t[1]] = {}
    color_dict[t[1]]['color_rgb'] = [int(_) for _ in int_str_to_lst(t[2])]
    color_dict[t[1]]['pos_tag'] = str_to_lst(t[3])
    color_dict[t[1]]['neg_tag'] = str_to_lst(t[4])
    color_dict[t[1]]['pct'] = 0.0

# Create main color objects
rgb_list = [_[1]['color_rgb'] for _ in color_dict.items()]

# Generating main color objects
main_colors = main_color(rgb_list, list(df_color['name']))



## Test
#
# Get colors from an image
@pytest.mark.parametrize('filename, main_colors',
                         [
                            ('space.png', main_colors)
                         ])
def test_getcolor(filename, main_colors):
    image = Img(filename = filename)
    image.getcolor(main_colors=main_colors)
    assert True
    
    
# Get a pool of quotes to choose from, based on mood and tag selected as well as image colors 
colors = Img(filename = 'space.png').getcolor(main_colors=main_colors)
img_color_dict = color_dict.copy()
for color in colors:
    img_color_dict[color[0]]['pct'] = color[1]

@pytest.mark.parametrize('store_mood, choose_tag, colors',
                         [
                            ('positive', 'ambition', img_color_dict)
                         ])
def test_get_quotes_pool(store_mood, choose_tag, colors):
    quotes_pool = get_quotes_pool(store_mood = store_mood, choose_tag = choose_tag, colors = colors)
    print('Screen out', len(quotes_pool), 'quotes')
    assert True


# Get n quotes from the pool of quotes
quotes_pool = get_quotes_pool(store_mood = 'positive', choose_tag = 'ambition', colors = img_color_dict)

@pytest.mark.parametrize('quotes_pool, alert_no_quote, n',
                         [
                            (quotes_pool, False, 5)
                         ])
def test_get_n_quotes(quotes_pool, alert_no_quote, n): 
    quotes_generated = get_n_quotes(quotes_pool, alert_no_quote, n)
    quotes_generated
    assert True
    



