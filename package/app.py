import dash
from flask_sqlalchemy import SQLAlchemy
import os

app = dash.Dash(__name__, url_base_pathname='/', title='PCV Listings', update_title=None)
app.server.config['DEBUG'] = False

# app.server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/pcv_listings_db'
app.server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('pcv_uri')

app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.app_context().push()
app.config['suppress_callback_exceptions'] = True
db = SQLAlchemy(app.server)
