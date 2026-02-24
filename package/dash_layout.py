from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
from package.app import app
from package.scrape import run_scraper

data = []
scrape_time = None


@callback(Output('apt-listings-table', 'data'), Output('scrape-time-monitor', 'children'), Input('interval-component', 'n_intervals'), State('scrape-time-monitor', 'children'))
def update_store(n_intervals, memory_scrape_time):
    if scrape_time is None:
        return no_update
    if memory_scrape_time != scrape_time:
        print("Inside callback. New scrape exists")
        print('memory_scrape_time', memory_scrape_time)
        print('scrape_time', scrape_time)
        return data, scrape_time
    else:
        return no_update

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

def update_trackers():
    global data, scrape_time
    data, scrape_time = run_scraper()

app.layout = html.Div(id='table-wrapper', style={'width': '80%', 'marginLeft': '8%', 'marginTop': '4%'}, children=[
                html.H3('Current Peter Cooper Village 2 Bedroom 2 Bathroom Listings'),
                html.Div(children=[
                    html.P('Last scrape:', style={'width': '10%', 'display': 'inline-block', 'marginTop': '0px'}),
                    html.P(id='scrape-time-monitor', style={'width': '20%', 'display': 'inline-block', 'marginTop': '0px'})
                ]),
                generate_table(),
                dcc.Interval(id='interval-component', interval=60000)
            ])
