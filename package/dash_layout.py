from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
from package.app import app
from package.scrape import run_scraper



listings, scrape_time = run_scraper()

@callback(Output('memory-output', 'data'), Input('memory-apartments', 'value'))
def filter_countries(countries_selected):
    if not countries_selected:
        return df.to_dict('records')
    dff = df[df['country'].isin(countries_selected)]
    return dff.to_dict('records')

@callback(Output('apt-listings-table', 'data'), Input('memory-output', 'data'))
def update_table(data):
    if data is None:
        return no_update
    return data

def generate_table():
    return dash_table.DataTable(
            id='apt-listings-table',
            data=listings,
            columns=[{'name': col, 'id': col} for col in listings[0].keys()],
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
                dcc.Store(id='memory-output'),
                html.H3('Current Peter Cooper Village 2 Bedroom 2 Bathroom Listings'),
                html.P('Last scrape: ' + scrape_time.strftime('%I:%M%p on %b %-d, %Y')),
                generate_table(),
            ])
