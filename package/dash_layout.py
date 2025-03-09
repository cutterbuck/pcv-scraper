from dash import html


def generate_layout():
    return html.Div([
            html.Div('hello world!', id='app-display')
    ])


app.layout = generate_app_layout()