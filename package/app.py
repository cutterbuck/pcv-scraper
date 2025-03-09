import dash
from flask_sqlalchemy import SQLAlchemy



app = dash.Dash(__name__, url_base_pathname='/', title='Cheap PCV Listings')
app.server.config['DEBUG'] = True
app.server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/pcv_listings_db'
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.server.app_context().push()
app.config['suppress_callback_exceptions'] = True
db = SQLAlchemy(app.server)
