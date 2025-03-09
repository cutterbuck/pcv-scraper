from dash import html
from package.app import app


def generate_layout():
    return html.Div([
            html.Div('hello world!', id='app-display')
    ])


app.layout = generate_layout()