from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
from package.app import app
from package.scrape import run_scraper
from datetime import datetime



@callback(Output('memory-store', 'data'), Input('interval-component', 'n_intervals'), State('memory-store', 'data'))
def update_store(n_intervals, data):
    now = datetime.now()
    today = now.date()

    if now > datetime(today.year, today.month, today.day, 3, 30, 0) and now < datetime(today.year, today.month, today.day, 6, 31, 0):
        new_listings = run_scraper()
        if new_listings == data:
            return data
        else:
            return new_listings
    else:
        return data

@callback(Output('apt-listings-table', 'data'), Input('memory-store', 'data'))
def update_table(data):
    return data

def generate_table():
    return dash_table.DataTable(
            id='apt-listings-table',
            columns=[{'name': col, 'id': col} for col in ["Building", "Floor", "Unit", "Rent", "Date Available"]],
            cell_selectable=False,
            style_cell={
                'font-family': "Open Sans, HelveticaNeue, Helvetica Neue, Helvetica, Arial, sans-serif",
                'text-align': 'center',
                'font-size': '12px',
                'font-weight': '500',
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

app.layout = html.Div(id='table-wrapper', style={'width': '80%', 'marginLeft': '8%', 'marginTop': '4%'}, children=[
                dcc.Store(id='memory-store', data=run_scraper()),
                html.H3('Current Peter Cooper Village 2 Bedroom 2 Bathroom Listings'),
                # html.P('Last scrape: ' + scrape_time.strftime('%I:%M%p on %b %-d, %Y')),
                generate_table(),
                dcc.Interval(id='interval-component', interval=960000)
            ])
