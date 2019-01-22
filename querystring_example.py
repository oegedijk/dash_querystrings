import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

# to set the DataPickerRange start/end dates:
from datetime import datetime, date, timedelta

# to generate the tinyurl:
from pyshorteners import Shortener

from querystring_methods import encode_state
from querystring_methods import parse_state
from querystring_methods import apply_value_from_querystring

app = dash.Dash(__name__)

app.config['suppress_callback_exceptions']=True

# The overall layout. Will be build properly in a callback triggered by the
# querystring
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-layout')
])


def build_layout(params):
    return html.Div([
        apply_value_from_querystring(params)(dcc.RadioItems)(
            id='country_radiobutton',
            options=[{'label': i, 'value': i}
                        for i in ['Canada', 'USA', 'Mexico']],
            value='Canada'
        ),

        html.Div(id='country_output', children='hello world!'),

        apply_value_from_querystring(params)(dcc.Dropdown)(
            id='club_multidropdown',
            options=[{'label': i, 'value': i}
                        for i in ['Ajax', 'Feyenoord', 'PSV', 'Heerenveen']],
            value=['Heerenveen'],
            multi=True
        ),
        apply_value_from_querystring(params)(dcc.DatePickerRange)(
                id='datepicker',
                start_date=date.today() - timedelta(days=7),
                end_date=date.today()
                ),
        apply_value_from_querystring(params)(html.Button)(
                'Submit', id='submit-button', n_clicks=0),
        html.Div(id='club_output'),

        html.Button('Generate Tiny URL', id='tinyurl-button'),

        html.Div(id='tiny_url')
    ])

# List of component (id, parameter) tuples. Can be be any parameter
# not just (., 'value'), and the value van be either a single value or a list:
component_ids = [
    ('country_radiobutton', 'value'),
    ('club_multidropdown', 'value'),
    ('datepicker', 'start_date'),
    ('submit-button', 'n_clicks')
]

# Turn the list of 4 (id, param) tuples into a list of
# one component id tuple (len=4) and one parameter tuple (len=4):
component_ids_zipped= list(zip(*component_ids))

@app.callback(Output('page-layout', 'children'),
              [Input('url', 'href')])
def page_load(href):
    """
    Upon page load, take the url, parse the querystring, and use the
    resulting state dictionary to build up the layout.
    """
    if not href:
        return []
    state = parse_state(href)
    return build_layout(state)


@app.callback(Output('url', 'search'),
              inputs=[Input(id, param) for (id, param) in component_ids])
def update_url_state(*values):
    """
    When any of the (id, param) values changes, this callback gets triggered.

    Passes the list of component id's, the list of component parameters
    (zipped together in component_ids_zipped), and the value to encode_state()
    and return a properly formed querystring.
    """
    return encode_state(component_ids_zipped, values)

@app.callback(
    Output('country_output', 'children'),
    [Input('country_radiobutton', 'value')])
def country_callback(country):
    """
    Display the country selected by `country_radiobutton` in the
    `country_output` html.Div:
    """
    return f'Country selected: {country}'


@app.callback(
    Output('club_output', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('club_multidropdown', 'value'),
     State('datepicker', 'start_date')])
def club_callback(n_clicks, clubs, startdate):
    """
    Display the clubs selected in `club_multidropdown` and the start_date
    of the `datepicker` in the `club_output` html.Div:
    """
    if n_clicks > 0:
        return f"""Clubs Selected: {str(clubs)}
                   Starting date: {str(startdate)}"""


@app.callback(Output('tiny_url', 'children'),
              [Input('tinyurl-button', 'n_clicks')],
              [State('url', 'search')])
def page_load(n_clicks, state):
    """
    Return a tinyurl whenever the `tinyurl-button` is clicked:
    """
    if not state:
        return "No url to shorten"
    if n_clicks > 0 and state:
        shortener = Shortener('Tinyurl')
        return shortener.short('http://127.0.0.1:8050' + state)


if __name__ == '__main__':
    app.run_server(debug=True)
