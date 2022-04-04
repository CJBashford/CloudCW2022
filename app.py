import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from dash.dependencies import Input, Output
from functions import get_stock_data, get_stock_info, create_card, dict_values, get_charts, get_headlines, company_list

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# STYLING

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 56,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "margin-top": "2rem"
}

# CREATING DATA

# Get List of tickers
sandp_list = company_list('United States')
ftse_list = company_list('United Kingdom')


# Create dictionary in {ticker: price history dataframe} format
sandp_frames = dict_values(sandp_list)
ftse_frames = dict_values(ftse_list)

news = get_headlines()

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("Stocks", className="ms-2")),
                    ],
                    justify="start",
                    className="g-0",
                ),
                style={"textDecoration": "none"},
            ),
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More", header=True),
                dbc.DropdownMenuItem("S&P 500", href="/sandp"),
                dbc.DropdownMenuItem("FTSE 100", href="/ftse"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
            ),
        ]
    ),
    color="dark",
    dark=True,
    fixed="top"
)

sidebar = html.Div(
    [
        html.H6("News Feed"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(f"{news['first'][0]}", href=f"{news['first'][1]}", target="_blank"),
                dbc.NavLink(f"{news['second'][0]}", href=f"{news['second'][1]}", target="_blank"),
                dbc.NavLink(f"{news['third'][0]}", href=f"{news['third'][1]}", target="_blank"),
                dbc.NavLink(f"{news['fourth'][0]}", href=f"{news['fourth'][1]}", target="_blank"),
                dbc.NavLink(f"{news['fifth'][0]}", href=f"{news['fifth'][1]}", target="_blank")
            ],
            vertical=True
            )
    ],
    style=SIDEBAR_STYLE,
)

# Create list of cards with charts

sandp_charts = get_charts(sandp_list, sandp_frames)
ftse_charts = get_charts(ftse_list, ftse_frames)
all_charts = sandp_charts + ftse_charts

# Create div that charts will be passed into

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
	dcc.Location(id="url"),
    navbar,
    sidebar,
    content
])

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return all_charts
    elif pathname =="/sandp":
    	return sandp_charts
    elif pathname == "/ftse":
        return ftse_charts
    else:
    	return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    	)

if __name__ == '__main__':
	app.run_server(debug=True)
