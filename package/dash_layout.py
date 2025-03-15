from dash import html, dash_table
from package.app import app
from package.models import Listing, db


def generate_layout():
    listings_query = db.session.query(Listing.building, Listing.floor, Listing.unit, Listing.status, Listing.current_rent, Listing.rent_change, Listing.initial_rent, Listing.last_updated, Listing.update_time, Listing.initial_posting_date, Listing.days_listed).order_by(Listing.id).all()
    listings = [{"Building": el[0], "Floor": el[1], "Unit": el[2], "Status": el[3], "Rent": el[4], "Change": el[5], "Initial Rent": el[6], "Last Update": el[7], "Time": el[8], "First Posted": el[9], "Days Available": el[10]} for el in listings_query]
    col_names = ["Building", "Floor", "Unit", "Status", "Rent", "Change", "Initial Rent", "Last Update", "Time", "First Posted", "Days Available"]
    columns = [{'name': c, 'id': c} for c in col_names]

    return html.Div(id='table-wrapper', style={'width': '80%', 'marginLeft': '8%', 'marginTop': '4%'}, children=[
            html.H4('Peter Cooper Village 2Bed/2Bath Listings:'),
            dash_table.DataTable(
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
    ])


app.layout = generate_layout()