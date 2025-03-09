from dash import html
from package.app import app
from package.models import Listing


def generate_layout():
    listings = Listing.query.all()
    return html.Div([
            html.Div('hello world!', id='app-display')
    ])


app.layout = generate_layout()