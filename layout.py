"""Holds dash layout."""

import dash_bootstrap_components as dbc
from dash import dcc, html

import data

scenario_options = data.get_scenarios()
scenario = dbc.Tabs(
    id="scenarios",
    children=[
        dbc.Tab(
            tab_id="scenario_single",
            label="Single Scenario",
            children=[
                html.Label("Scenario:"),
                dcc.Dropdown(
                    id="scenario",
                    options=scenario_options,
                    value=scenario_options[0],
                    clearable=False,
                ),
            ],
        ),
        dbc.Tab(
            tab_id="scenario_comparison",
            label="Scenario Comparison",
            children=[
                html.Div(
                    [
                        html.Label("Scenario 1:"),
                        dcc.Dropdown(
                            id="scenario_1",
                            options=scenario_options,
                            value=scenario_options[0],
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Label("Scenario 2:"),
                        dcc.Dropdown(
                            id="scenario_2",
                            options=scenario_options,
                            value=scenario_options[1],
                            clearable=False,
                        ),
                    ],
                ),
            ],
        ),
    ],
    style={"margin-bottom": "10px"},
)

scenario_description = data.get_scenario_text()
scenario_text = html.Div([
    dcc.Textarea(
        id='textarea-scenario',
        value=scenario_description[scenario_options[0]],
        style={'width': '100%', 'height': 100, "resize": "none"},
        disabled=True,
        cols=1,
        rows=3
    ),
])

year_options = data.get_years()
year = html.Div(
    [
        html.Label("Target Year:"),
        dcc.Slider(
            id="year",
            step=None,
            marks={year: str(year) for year in year_options},
            value=year_options[0],
        ),
    ],
    style={"margin-bottom": "10px", "margin-top": "10px"},
)
requirements = html.Div(
    [
        html.Label("Requirements:"),
        dbc.RadioItems(
            id="requirement",
            options=[
                {"label": "Area", "value": "area"},
                {"label": "Water", "value": "water"},
            ],
            value="area",
        ),
    ],
    style={"margin-bottom": "10px"},
)
unit = html.Div(
    [
        html.Label("Unit:"),
        dbc.RadioItems(
            id="unit",
            options=[
                {"label": "km²", "value": "area_km2"},
                {"label": "Percentage", "value": "rel"},
                {"label": "Olympic Soccer Fields (105 x 68 m²)", "value": "oly_field"},
            ],
            value="rel",
        ),
    ],
)
criteria_options = data.get_criteria("area")
criteria = html.Div(
    [
        html.Label("Criteria for requirements:"),
        dcc.Checklist(
            id="criteria",
            options=criteria_options,
            value=criteria_options,
            #multi=True,
            labelStyle={'display': 'block'},
            inputStyle={"margin-right": "5px"},
        ),
    ],
    style={"margin-top": "10px"},
)

region = html.Section(
    title="Region",
    children=[
        dcc.Graph(
            id="region",
        ),
    ],
)
atlas = dbc.Row(
    [
        dbc.Col(
            id="col_choropleth_1",
            children=[
                dcc.Graph(
                    id="choropleth_1",
                ),
            ],
        ),
        dbc.Col(
            id="col_choropleth_2",
            children=[
                dcc.Graph(id="choropleth_2", config={"displayModeBar": False}),
            ],
        ),
    ],
)
controls = html.Section(
    title="Settings",
    children=[scenario, year, requirements, unit, criteria],
)

DEFAULT_LAYOUT = dbc.Container(
    [
        # row with choropleth map
        dbc.Row(
            [
                dbc.Col(
                    atlas,
                    className="col-8",
                    style={"margin-top": "10px"},
                ),
                dbc.Col(controls, className="col-3", style={
                        "border": "1.5px black solid",
                        "background-color": "rgba(0,0,0,0)",
                        "margin-left": "20px",
                        "margin-right": "50px",
                        "margin-top": "10px",
                        "margin-bottom": "50px",
                        },),
            ],
        ),
        dbc.Row(dbc.Col(scenario_text, className="col-7", style={
                        "margin-left": "20px",
                        "margin-right": "50px",
                        "margin-top": "10px",
                        "margin-bottom": "50px",
                        })
                ),
        # row with bar chart
        dbc.Row(dbc.Col(region, className="col-9"), style={"margin-right": "150px"}),
    ],
    fluid=True,
)
