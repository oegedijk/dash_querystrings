import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

from urllib.parse import urlparse, parse_qs, urlencode

import ast

from datetime import datetime, date, timedelta

from pyshorteners import Shortener

def encode_state(component_ids_zipped, values):
    """
    return a urlencoded string that encodes the current state of the app
    (as identified by (component_ids, params)+values

    First encodes as a list of tuples of tuples of :
    (component_id, (parameter, value))

    This then gets encoded by urlencode as two separate querystring parameters
    e.g. ('tabs', ('value', 'tab1')) will get encoded as:
          ?tabs=value&tabs=tab1
    """

    statelist = [(component_ids_zipped[0][i],
                    (component_ids_zipped[1][i],
                    values[i]))
                    for i in range(len(values))
                    if  values[i] is not None]

    params = urlencode(statelist,  doseq=True)
    return f'?{params}'


def parse_state(url):
    """
    Returns a dict that summarizes the state of the app at the time that the
    querystring url was generated.

    The querystring parameters come in pairs (see above), e.g.:
              ?tabs=value&tabs=cs_tab

    This will then be encoded as dictionary with the component_id as key
    (e.g. 'tabs') and a list (param, value) pairs (e.g. ('value', 'cs_tab')
    for that component_id as the item.

    lists (somewhat hackily detected by the first char=='['), get evaluated
    using ast.

    Numbers are appropriately cast as either int or float.
    """

    parse_result = urlparse(url)

    statedict = parse_qs(parse_result.query)
    if statedict:
        for key, value in statedict.items():
            statedict[key] = list(map(list, zip(value[0::2], value[1::2])))
            # go through every parsed value pv and check whether it is a list
            # or a number and cast appropriately:
            for pv in statedict[key]:
                # if it's a list
                if isinstance(pv[1], str) and pv[1][0]=='[':
                    pv[1] = ast.literal_eval(pv[1])

                #if it's a number
                if (isinstance(pv[1], str) and
                    pv[1].lstrip('-').replace('.','',1).isdigit()):

                    if pv[1].isdigit():
                        pv[1] = int(pv[1])
                    else:
                        pv[1] = float(pv[1])
    else: #return empty dict
        statedict = dict()
    return statedict


def apply_value_from_querystring(params):
    """
    Funky function wrapper that looks up the component_id in the
    querystring parameter statedict `params`, and if it finds it, loops
    through the (param, value) combinations in the (item) list
    and assign the right value to the right parameter.

    Every component that is saved in the querystring needs to be wrapped
    in this function in order for the saved parameters to be assigned
    during loading.
    """
    def wrapper(func):
        def apply_value(*args, **kwargs):
            if 'id' in kwargs and kwargs['id'] in params:
                param_values = params[kwargs['id']]
                for pv in param_values:
                    kwargs[pv[0]] = pv[1]
            return func(*args, **kwargs)
        return apply_value
    return wrapper

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

component_ids = [
    ('country_radiobutton', 'value'),
    ('club_multidropdown', 'value'),
    ('datepicker', 'start_date'),
    ('submit-button', 'n_clicks')
]

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
    return encode_state(component_ids_zipped, values)

@app.callback(
    Output('country_output', 'children'),
    [Input('country_radiobutton', 'value')])
def country_callback(country):
    return f'Country selected: {country}'


@app.callback(
    Output('club_output', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('club_multidropdown', 'value'),
     State('datepicker', 'start_date')])
def club_callback(n_clicks, clubs, startdate):
    if n_clicks > 0:
        return f"""Clubs Selected: {str(clubs)}
                   Starting date: {str(startdate)}"""


@app.callback(Output('tiny_url', 'children'),
              [Input('tinyurl-button', 'n_clicks')],
              [State('url', 'search')])
def page_load(n_clicks, state):
    if not state:
        return "No url to shorten"
    if n_clicks > 0 and state:
        shortener = Shortener('Tinyurl')
        return shortener.short('http://127.0.0.1:8050' + state)


if __name__ == '__main__':
    app.run_server(debug=True)
