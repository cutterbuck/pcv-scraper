import dash

app = dash.Dash(__name__, url_base_pathname='/', title='PCV Apartments', update_title=None)
app.server.config['DEBUG'] = True
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['suppress_callback_exceptions'] = True
