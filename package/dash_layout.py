from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
from package.app import app
from package.models import Listing, db



def get_data():
    available = db.session.query(Listing.building, Listing.floor, Listing.unit, Listing.status, Listing.current_rent, Listing.rent_change, Listing.initial_rent, Listing.last_updated, Listing.update_time, Listing.initial_posting_date, Listing.days_listed).filter(Listing.status == 'available').order_by(Listing.current_rent).all()
    unavailable = db.session.query(Listing.building, Listing.floor, Listing.unit, Listing.status, Listing.current_rent, Listing.rent_change, Listing.initial_rent, Listing.last_updated, Listing.update_time, Listing.initial_posting_date, Listing.days_listed).filter(Listing.status == 'unavailable').order_by(Listing.current_rent).all()
    all_listings = available + unavailable
    return [{"Building": el[0], "Floor": el[1], "Unit": el[2], "Status": el[3], "Rent": el[4], "Change": el[5], "Initial Rent": el[6], "Last Update": el[7].strftime('%m/%d/%Y'), "Time": el[8], "First Posted": el[9].strftime('%m/%d/%Y'), "Days Available": el[10]} for el in all_listings]

def generate_table():
    print("creating table")
    listings = get_data()
    col_names = ["Building", "Floor", "Unit", "Status", "Rent", "Change", "Initial Rent", "Last Update", "Time", "First Posted", "Days Available"]
    columns = [{'name': c, 'id': c} for c in col_names]
    return dash_table.DataTable(
            id='apt-listings-table',
            data=listings,
            columns=[{'name': c, 'id': c} for c in col_names],
            merge_duplicate_headers=True,
            cell_selectable=False,
            style_cell={
                'font-family': "Open Sans, HelveticaNeue, Helvetica Neue, Helvetica, Arial, sans-serif",
                'text-align': 'center',
                'font-size': '12px',
                'font-weight': '400',
                'line-height': '1.6',
                'padding': '2px 0px 2px 0px',
                'width': '4%',
                'border': '1px 0px 1px 0px solid #E1E1E1'
            },
            style_data_conditional=[{
                'if': {'row_index': 'even'},
                'backgroundColor': 'rgb(221, 230, 240)',
            }],
            style_header={
                'backgroundColor': 'rgb(255, 255, 255)',
                'color': 'rgb(50, 50, 50)',
                'border': 'none',
                'fontSize': '10px',
                'padding': '5px 5px 5px 5px',
                'fontWeight': '600',
                'height': '27px'
            },
            css=[{'selector': '.dash-spreadsheet tr', 'rule': 'height: 23px;'}],
    )


@callback(
    Output('apt-listings-table', 'data'),
    Input('live-interval', 'n_intervals'),
    State('apt-listings-table', 'data')
)
def update_metrics(n_intervals, data):
    print("new data check")
    new_data = get_data()
    if new_data == data:
        return no_update
    else:
        return new_data

app.layout = html.Div(id='table-wrapper', style={'width': '80%', 'marginLeft': '8%', 'marginTop': '4%'}, children=[
                html.H4('Peter Cooper Village 2Bed/2Bath Listings:'),
                generate_table(),
                dcc.Interval(
                    id='live-interval',
                    interval=300000, # in milliseconds
                    n_intervals=0
                )
            ])
