from dash import html, dcc, Input, Output, State, callback, dash_table
from package.app import app
from package.scrape import run_scraper
from datetime import datetime
from zoneinfo import ZoneInfo


@callback(Output('memory-store', 'data'), Output('scrape-time-monitor', 'children'), Input('interval-component', 'n_intervals'), State('memory-store', 'data'), State('scrape-time-monitor', 'children'))
def update_store(n_intervals, data, last_scrape_time):
    now = datetime.now().astimezone(ZoneInfo('America/New_York'))
    today = now.date()

    # if now > datetime(today.year, today.month, today.day, 3, 30, 0) and now < datetime(today.year, today.month, today.day, 6, 31, 0):
    if now > datetime(today.year, today.month, today.day, 18, 30, 0).astimezone(ZoneInfo('America/New_York')) and now < datetime(today.year, today.month, today.day, 18, 59, 0).astimezone(ZoneInfo('America/New_York')):
        print("Checking for new apartments:")
        new_listings, new_scrape_time = run_scraper()
        if new_listings == data:
            return data, new_scrape_time
        else:
            return new_listings, new_scrape_time
    else:
        return data, last_scrape_time

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

data, first_scrape = run_scraper()

app.layout = html.Div(id='table-wrapper', style={'width': '80%', 'marginLeft': '8%', 'marginTop': '4%'}, children=[
                dcc.Store(id='memory-store', data=data),
                html.H3('Current Peter Cooper Village 2 Bedroom 2 Bathroom Listings'),
                html.Div(children=[
                    html.P('Last scrape:', style={'width': '10%', 'display': 'inline-block', 'marginTop': '0px'}),
                    html.P(first_scrape.strftime('%I:%M%p on %b %-d, %Y'), id='scrape-time-monitor', style={'width': '20%', 'display': 'inline-block', 'marginTop': '0px'})
                ]),
                generate_table(),
                dcc.Interval(id='interval-component', interval=300000)
            ])
