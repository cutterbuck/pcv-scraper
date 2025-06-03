import dash


app = dash.Dash(__name__, url_base_pathname='/', title='Aerok Capital Advisors', update_title=None)
app.server.config['DEBUG'] = True

app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.app_context().push()
app.config['suppress_callback_exceptions'] = True
