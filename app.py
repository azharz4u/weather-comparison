import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__)
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')

# retrieve data
temp_df = pd.DataFrame(
    data={
        'Bristol': [4, 3, 2, 4],
        'London': [5, 3, 3, 6],
        'Auckland': [8, 4, 7, 9],
        'Wellington': [10, 9, 6, 8]
    },
    index=['Q1', 'Q2', 'Q3', 'Q4'])

# construct layout
app.title = "Climate comparison"
app.layout = html.Div([
    html.H1("Climate comparison"),
    dcc.Markdown("Select cities to compare their climates."), dcc.Dropdown(
        id='city-select',
        options=[{
            'label': k,
            'value': k
        } for k in temp_df.columns],
        value=['Bristol', 'London'],
        multi=True), dcc.Graph(id='graphs')
])


# create charts from inputs
@app.callback(
    dash.dependencies.Output('graphs', 'figure'),
    [dash.dependencies.Input('city-select', 'value')])
def update_figure(cities):
    traces = []
    for city in cities:
        traces.append(go.Scatter(x=temp_df.index, y=temp_df[city], name=city))
    layout = go.Layout(title="Temperature")

    figure = go.Figure(data=go.Data(traces), layout=layout)
    return figure


external_css = [
    "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f4126569a3440aae611bbef1d7a5dd/stylesheet.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
