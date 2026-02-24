import dash

app = dash.Dash(__name__, url_base_pathname='/', title='PCV Apartments', update_title=None)
app.config['suppress_callback_exceptions'] = True
