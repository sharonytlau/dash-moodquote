# <editor-fold desc="import modules">
from algorithms.image import *
from algorithms.color import *
import json
import os
import datetime
import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate




# </editor-fold>

# <editor-fold desc="initialization">
cwd = os.getcwd()
pd.set_option('display.max_columns', None)
pd.set_option('mode.chained_assignment', None)

# %%
## Color data
df_color = pd.read_csv('data/color_tag.csv')


def int_str_to_lst(value):
    return list(value.strip('[]').split(', '))


def str_to_lst(value):
    return list(value.strip('[]').strip("''").split("', '"))

# print(df_color.head(3))
# print(df_color.columns) # ['name', 'rgb', 'pos_tag', 'neg_tag']

color_dict = {}
for t in df_color.itertuples():
    color_dict[t[1]] = {}
    color_dict[t[1]]['color_rgb'] = [int(_) for _ in int_str_to_lst(t[2])]
    color_dict[t[1]]['pos_tag'] = str_to_lst(t[3])
    color_dict[t[1]]['neg_tag'] = str_to_lst(t[4])
    color_dict[t[1]]['pct'] = 0.0
# print(json.dumps(color_dict, indent=4, sort_keys=True))

# create main color objects
rgb_list = [_[1]['color_rgb'] for _ in color_dict.items()]
main_colors = main_color(rgb_list, list(df_color['name']))

# %%
## Quotes data
df_quotes = pd.read_csv('data/all_quotes_w_sentimentalScore.csv')
df_quotes = df_quotes[df_quotes['Likes'] != -1]
df_quotes = df_quotes[df_quotes['length'] <= 55]

# print(df_quotes.head())
# print(df_quotes.tail())

# %%
## Get current date
today = datetime.date.today()
formatted_today = today.strftime('%y%m%d')
random_state = int(formatted_today)

# %%
## Get dropdown options
all_pos_tags = []
all_neg_tags = []

for tags in df_color['pos_tag']:
    if type(tags) != list:
        all_pos_tags.extend(tags.strip('[]').strip("''").split("', '"))
    else:
        all_pos_tags.extend(tags)
tag_pos = list(set(all_pos_tags))
tag_pos.sort()
for tags in df_color['neg_tag']:
    if type(tags) != list:
        all_neg_tags.extend(tags.strip('[]').strip("''").split("', '"))
    else:
        all_neg_tags.extend(tags)
tag_neg = list(set(all_neg_tags))
tag_neg.sort()

tag_all = {'pos': tag_pos, 'neg': tag_neg}

tag_dropdown_pos = [{'label': tag, 'value': tag} for tag in tag_all['pos']]
tag_dropdown_neg = [{'label': tag, 'value': tag} for tag in tag_all['neg']]
tag_dropdown_pop = [{'label': 'popular-quote', 'value': 'popular-quote'}]

tag_dropdown_all = tag_dropdown_pos + tag_dropdown_neg + tag_dropdown_pop
tag_dropdown_all = sorted(tag_dropdown_all, key=lambda k: k['label'])

# </editor-fold>

# <editor-fold desc="dash app">
external_stylesheets = [dbc.themes.BOOTSTRAP,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

# <editor-fold desc="app components">
button_classname = 'mood-btn'
mood_buttons = html.Div(
    [
        dbc.Button(
            # 'Positive',
            html.I(className="far fa-grin-beam"),
            # '😄',
            className=button_classname,
            id='button_positive'),
        dbc.Button(
            # 'Neutral',
            html.I(className="far fa-meh"),
            # '😐',
            className=button_classname,
            id='button_neutral'),
        dbc.Button(
            # 'Negative',
            html.I(className="far fa-frown-open"),
            # '🙁',
            className=button_classname,
            id='button_negative'),
    ], className='mood-btn-group')


quote_today = df_quotes.sample(random_state=random_state).iloc[0]



# </editor-fold>


# <editor-fold desc="app callbacks">
# %%
# Show uploaded image
@app.callback(
    [Output('uploaded-image', 'src'),
     # Output('uploaded-image', 'className'),
     Output('store-color', 'data'),
     Output('image-upload-message', 'is_open')
     # Output('image-upload', 'className')
     ],
    [Input('image-upload', 'contents')],
    [State('image-upload', 'filename')],
    prevent_initial_call=True)
def show_image(contents, filename):
    if filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png', 'svg', 'gif']:
        return None, None, True
    else:
        string = contents.split(";base64,")[-1]
        user_img = Img(string)
        user_img.b64_to_pil()
        colors = user_img.getcolor(main_colors=main_colors)
        img_color_dict = color_dict.copy()
        for color in colors:
            img_color_dict[color[0]]['pct'] = color[1]
        # print(user_img)
        # print(json.dumps(img_color_dict, indent=4, sort_keys=True))
        return contents, img_color_dict, False


@app.callback([Output('button_positive', "children"),
               Output('button_neutral', "children"),
               Output('button_negative', "children")],
              [Input('button_positive', "n_clicks"),
               Input('button_neutral', "n_clicks"),
               Input('button_negative', "n_clicks")])
def set_active(*args):
    ctx = dash.callback_context.triggered
    fa_1 = html.I(className="far fa-grin-beam mood-fa")
    fa_2 = html.I(className="far fa-meh mood-fa")
    fa_3 = html.I(className="far fa-frown-open mood-fa")
    emoji_1 = '😄'
    emoji_2 = '😐'
    emoji_3 = '🙁'
    if not ctx or not any(args):
        return [fa_1, fa_2, fa_3]

    ## get id of triggering button
    button_id = ctx[0]["prop_id"].split(".")[0]
    if button_id == 'button_positive':
        return emoji_1, fa_2, fa_3
    elif button_id == 'button_neutral':
        return fa_1, emoji_2, fa_3
    else:
        return fa_1, fa_2, emoji_3


## Update dropdown options
@app.callback([Output('choose_tag', 'options'),
               Output('store_mood', 'data')],
              [Input('button_positive', 'n_clicks'),
               Input('button_neutral', 'n_clicks'),
               Input('button_negative', 'n_clicks')],
              prevent_initial_call=True)
def update_dropdown(click_positive, click_neutral, click_negative):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'button_positive' in changed_id:
        store_mood = 'positive'
        options = tag_dropdown_pos + tag_dropdown_pop
        options = sorted(options, key=lambda k: k['label'])
    elif 'button_negative' in changed_id:
        store_mood = 'negative'
        options = tag_dropdown_all
    else:
        store_mood = 'neutral'
        options = tag_dropdown_all
    return options, store_mood

@app.callback(
    Output('choose_tag', 'className'),
    [Input('choose_tag', 'value')])
def dropdown_style(choose_tag):
    if choose_tag is not None:
        return 'tag-dropdown chosen'
    else:
        return 'tag-dropdown'

## Show alert
@app.callback([Output('search_alert', 'children'),
               Output('search_alert', 'is_open'),
               Output('search_alert', 'className')],
              [Input('search_button', 'n_clicks')],
              [State('store_mood', 'data'),
               State('choose_tag', 'value'),
               State('store-color', 'data')],
              prevent_initial_call=True)
def show_alert(n_clicks, store_mood, choose_tag, colors):
    if colors is None:
        alert_is_open = True
        alert_class = 'alert-message alert-danger' # 'd-flex apply-alert alert-danger'
        if store_mood is None:
            alert_message = 'Please upload an image and select a mood for quotes'
        else:
            alert_message = 'Please upload an image'
    else:
        if store_mood is None:
            alert_is_open = True
            alert_class = 'alert-message alert-danger'
            alert_message = 'Please select a mood for quotes'
        else:
            alert_is_open = False
            alert_message = None
            alert_class = 'alert-message alert-danger'
    return alert_message, alert_is_open, alert_class


## Generate quotes
def get_num_tags_contained(quote_tags, colors):
    wt_num_tags_contained = 0
    for color in colors.values():
        color_tags = color['pos_tag'] + color['neg_tag']
        wt_num_tags_contained += color['pct'] * sum([color_tag in quote_tags for color_tag in color_tags])
    return wt_num_tags_contained


def if_contain_tag(quote_tags, choose_tag):
    bool = choose_tag in quote_tags
    return bool


def get_quotes_pool(store_mood, choose_tag, colors):
    quotes_pool = df_quotes[df_quotes['polarity'] == store_mood]
    if choose_tag is not None:
        quotes_pool = quotes_pool[quotes_pool['Clean_tags'].apply(if_contain_tag, choose_tag=choose_tag)]
    quotes_pool['#_tags_contained'] = quotes_pool['Clean_tags'].apply(get_num_tags_contained, colors=colors)
    if sum(quotes_pool['#_tags_contained']) != 0:
        quotes_pool = quotes_pool[quotes_pool['#_tags_contained'] != 0]
    quotes_pool.sort_values(by=['#_tags_contained', 'Likes'], ascending=False, inplace=True)
    return quotes_pool


def get_n_quotes(quotes_pool, alert_no_quote, n):
    def append_generated_quotes(quotes_pool):
        quotes_generated = []
        for i in range(len(quotes_pool)):
            quote = quotes_pool.iloc[i]['Quote']
            author = quotes_pool.iloc[i]['Author']
            try:
                if np.isnan(quotes_pool.iloc[i]['Book']):
                    book = ''
            except:
                book = ', ' + quotes_pool.iloc[i]['Book']
            quotes_generated.append(quote + ' ----' + author + book)
        return quotes_generated

    if alert_no_quote:
        authors = []
        quotes_generated = []
        for i in range(len(quotes_pool)):
            if len(quotes_generated) < n:
                author = quotes_pool.iloc[i]['Author']
                if author not in authors:
                    quote = quotes_pool.iloc[i]['Quote']
                    authors.append(author)
                    try:
                        if np.isnan(quotes_pool.iloc[i]['Book']):
                            book = ''
                    except:
                        book = ', ' + quotes_pool.iloc[i]['Book']
                    quotes_generated.append(quote + ' ----' + author + book)
            else:
                break
    else:
        if len(quotes_pool) <= n:
            quotes_generated = append_generated_quotes(quotes_pool)
        else:
            if quotes_pool['Author'].nunique() >= n:
                quotes_pool = quotes_pool.drop_duplicates(subset=['Author'], keep='first')
                quotes_pool = quotes_pool.iloc[:n]
                quotes_generated = append_generated_quotes(quotes_pool)
            else:
                unique_first = quotes_pool.drop_duplicates(subset=['Author'], keep='first')
                quotes_generated = append_generated_quotes(unique_first)
                rest_pool = quotes_pool.append(unique_first).drop_duplicates(keep=False)
                rest_pool = rest_pool.iloc[:(n - len(quotes_generated))]
                quotes_generated.extend(append_generated_quotes(rest_pool))
    return quotes_generated


@app.callback([
    Output('quotes-control', 'style'),
    Output('generate_quotes_1', 'children'),
    Output('generate_quotes_1', 'className'),
    Output('generate_quotes_2', 'children'),
    Output('generate_quotes_2', 'className'),
    Output('store-quotes-count', 'data'),
    Output('store-quotes', 'data'),
    Output('store-bool_no_quote', 'data')],
    [Input('search_button', 'n_clicks'),
     Input("previous-quote", 'n_clicks'),
     Input("next-quote", 'n_clicks'),
     Input('image-upload', 'last_modified')],
    [State('store_mood', 'data'),
     State('choose_tag', 'value'),
     State('store-color', 'data'),
     State('store-quotes-count', 'data'),
     State('store-quotes', 'data')],
    prevent_initial_call=True)
def generate_quotes(n_clicks, back, nxt, upload_stamp, store_mood, choose_tag, colors, history, quotes):
    button_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'image-upload':
        return {'display': 'none'}, '', 'd-none', '', 'image-quote', history, '', False
    elif colors is None or store_mood is None:
        raise PreventUpdate
    else:
        classname = 'image-quote-left'
        if button_id == 'search_button':
            quotes_pool = get_quotes_pool(store_mood, choose_tag, colors)
            alert_no_quote = True if sum(quotes_pool['#_tags_contained']) == 0 else False
            quotes_generated = get_n_quotes(quotes_pool, alert_no_quote, n=5)
            history = {"index": 0, "back": 0, "next": 0, "id":'generate_quotes_1'}
        else:
            if back > history["back"]:
                history["back"] = back
                history['index'] -= 1
                classname = 'image-quote-right'
                if history['index'] < 0:
                    history['index'] = 4
            elif nxt > history["next"]:
                history["next"] = nxt
                history['index'] += 1
                if history['index'] > 4:
                    history['index'] = 0
            quotes_generated = quotes
            alert_no_quote = False
        quote_display = quotes_generated[history['index']]
        if history['id'] == 'generate_quotes_1':
            history['id'] = 'generate_quotes_2'
            class_1 = 'd-none'
            class_2 = classname
            children_1 = None
            children_2 = quote_display
        else:
            history['id'] = 'generate_quotes_1'
            class_1 = classname
            class_2 = 'd-none'
            children_2 = None
            children_1 = quote_display
        # print(quotes_generated)
        return {'display': 'flex'}, children_1, class_1, children_2, class_2, history, quotes_generated, alert_no_quote

## Show alert if no quotes matching the colors
@app.callback([Output('alert_no_quotes', 'is_open'),
               Output('alert_no_quotes', 'children')],
              [Input('store-bool_no_quote', 'data')])
def no_quotes_alert(alert_no_quote):
    if alert_no_quote:
        alert_is_open = True
        alert_message = "Oops! There are no quotes matching your photo's colors. We have some popular quotes for you based on the mood and tag you selected. Check it out!"
    else:
        alert_is_open = False
        alert_message = None
    return  alert_is_open, alert_message

# </editor-fold>


# <editor-fold desc="app layout">
app.layout = html.Div(
    [dcc.Store(id="store-color"),
     dcc.Store(id="store_mood"),
     dcc.Store(id="store-quotes"),
     dcc.Store(id="store-quotes-count"),
     dcc.Store(id="store-bool_no_quote"),

     dbc.Row(
         [
             dbc.Row(

                 [
                     html.Div(
                         [
                             html.I(className="fa fa-quote-right brand-icon"),
                             html.P('MOODQUOTE', className='brand-text'),
                             html.P('- Jiaying Yan, Ying Tung Lau', className='title-author'),
                             html.P('Quote Maker', className='title-nav-1'),
                             html.P('Quote of the Day', className='title-nav-2')
                         ], className='brand-wrapper')
                 ], className='background-row'),
             html.Div(
                 [
                     html.H1('a personalized quote maker', className='r1-head-1'),
                     html.P(
                         'Looking for quotes that pair with your photos to post on social media or other websites? '
                         'Our intelligent tool will analyze your photo and generate good quotes that fit your mood,'
                         'with a rich database of 10k quotes from 100+ themes.', className='r1-p'),
                     html.A(
                         [
                             dbc.Button(
                                 [
                                     html.Span('Start\u00a0\u00a0'),
                                     html.Span(html.I(className="fas fa-long-arrow-alt-down"))],
                                 id='anchor-makequote-btn', className='anchor-makequote-btn', n_clicks=0,
                                 color='light')],
                         href='#row-2-target',
                         className='anchor-makequote'),
                 ], className='intro-wrapper'),
         ], className='app-row-1'),
     dbc.Row(
         [
             html.A(id='row-2-target', className='anchor-target'),
             html.Img(src='assets/image_placeholder.jpg', className='image-placeholder'),
             html.Div([
                 html.Img(src='', id='uploaded-image'),

                 html.Div(
                     [
                         html.Div([
                             dbc.Button('<', id='previous-quote',
                                        className='quote-btn-left',
                                        n_clicks=0),
                             html.Div(id='generate_quotes_2', className='image-quote'),
                             html.Div(id='generate_quotes_1', className='image-quote'),
                             dbc.Button('>', id='next-quote',
                                        className='quote-btn-right',
                                        n_clicks=0)
                         ], className='quotes-control'),
                     ], id='quotes-control', className='quotes-control-wrapper', style={'display': 'none'}),
                 html.Div([
                     html.Div(
                         [
                             html.Div([
                                 dbc.Label("MOOD", html_for='mood-btn-group',
                                           className='input-label'),
                                 mood_buttons], className='input-panel-r2'),
                             html.Div(
                                 [
                                     dbc.Label("THEME", html_for='choose_tag', className='input-label'),
                                     dcc.Dropdown(
                                         id='choose_tag',
                                         options=tag_dropdown_all,
                                         placeholder='(optional)',
                                         optionHeight=55,
                                         className='tag-dropdown')], className='input-panel-r3'),
                             html.Div(
                                 [
                                     dcc.Upload(
                                         children=html.A(
                                             'Upload your Own Image \n'
                                             '(Select or Drag and Drop)'),
                                         multiple=False,
                                         id='image-upload',
                                         className='btn-light upload-btn'),
                                     dbc.Alert('This file is not a supported image - please only upload JPG,PNG,GIF or SVG type.',id='image-upload-message', is_open=False,duration=4500, dismissable=True,
                                               fade=True, className='alert-message alert-warning'),
                                     dbc.Alert(id='search_alert', is_open=False, duration=4500, dismissable=True,
                                               fade=True, className='alert-message'),
                                     dbc.Alert(id='alert_no_quotes', is_open=False,
                                               className='alert-message alert-info', fade=True, dismissable=True),
                                 ], className='input-panel-r1'),
                             dbc.Button(
                                 id='search_button',
                                 children=html.I(className='fas fa-search'),
                                 n_clicks=0,
                                 className='search-btn'),
                             html.Div(className='input-panel-border'),
                         ],
                         className='input-panel-wrapper'),
                 ], className='image-c2'),
             ], className='image-container-wrapper'),
         ],
         className='app-row-2'),
     dbc.Row(
         [
             html.Div([
                 html.Div([
                     html.Div([
                         html.I(className="fa fa-quote-left today-quote-icon"),
                         html.P('QUOTE OF THE DAY', className='today-quote-title'),
                     ], className='today-quote-title-wrapper'),
                     html.P([
                         quote_today['Quote'],
                         html.Span(' ---- ' + quote_today['Author'], className='text-nowrap')],
                         className='today-quote-content-wrapper'),
                 ], className='today-quote-wrapper')
             ], className='r3-c'),
         ], className='app-row-3'),
     dbc.Row(
         [
         ], className='app-row-4')
     ], className='app-body')
# </editor-fold>

if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)
# </editor-fold>
