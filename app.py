"""Main Dash app to display charts"""

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.tools import make_subplots
from scrape_data import data_test_harness  # local import

APP = dash.Dash(__name__)
SERVER = APP.server
SERVER.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')

# city options
CITIES = ['London', 'Bristol', 'Auckland', 'Wellington']

# construct layout
APP.title = "Climate comparison"
APP.layout = html.Div([
    html.H1("Climate comparison"),
    dcc.Markdown("Select cities to compare their climates."), dcc.Dropdown(
        id='city-select',
        options=[{
            'label': k,
            'value': k
        } for k in CITIES],
        value=['Bristol', 'London'],
        multi=True), dcc.Graph(id='graphs')
])


def figure_template():
    """Create figure template layout, ready for the data."""
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Daily maximum temperature", "Daily minimum temperature",
            "Precipitation"
        ])
    fig['layout'].update(
        dict(
            width=500,
            height=800,
            yaxis1=go.YAxis(title="Mean daily high"),
            yaxis2=go.YAxis(title="Mean daily low"),
            yaxis3=go.YAxis(title="Average monthly precipitation"),
            xaxis1=go.XAxis(title="Month (Northern hemisphere)")))

    return fig


# create charts from inputs
@APP.callback(
    dash.dependencies.Output('graphs', 'figure'),
    [dash.dependencies.Input('city-select', 'value')])
def update_figure(cities):
    """Update charts with data"""
    fig = figure_template()
    data = data_test_harness(cities)  # to replace with real scraper
    traces = []
    for city in cities:
        df = data[city]
        traces.append(
            go.Scatter(x=df.index, y=df['high'], name=city, yaxis='y1'))
        traces.append(
            go.Scatter(x=df.index, y=df['low'], name=city, yaxis='y2'))
        traces.append(
            go.Scatter(
                x=df.index, y=df['precipitation'], name=city, yaxis='y3'))

    fig['data'] = go.Data(traces)
    return fig


external_css = [
    "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f4126569a3440aae611bbef1d7a5dd/stylesheet.css"
]

for css in external_css:
    APP.css.append_css({"external_url": css})

if __name__ == '__main__':
    APP.run_server(debug=True)
