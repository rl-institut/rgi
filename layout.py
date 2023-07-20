"""Holds dash layout."""

import dash_bootstrap_components as dbc
from dash import dcc, html

import controls

scenario_options = controls.get_scenarios()
scenario = dbc.Tabs(
    id="scenarios",
    children=[
        dbc.Tab(
            label="Single Scenario",
            children=[
                html.Label("Scenario:"),
                dcc.Dropdown(
                    id="scenario_1",
                    options=scenario_options,
                ),
            ],
        ),
        dbc.Tab(
            label="Scenario Comparison",
            children=[
                html.Div(
                    [
                        html.Label("Scenario 1:"),
                        dcc.Dropdown(
                            id="scenario_1",
                            options=scenario_options,
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Label("Scenario 2:"),
                        dcc.Dropdown(
                            id="scenario_2",
                            options=scenario_options,
                        ),
                    ],
                ),
            ],
        ),
    ],
)
year = html.Div(
    [
        html.Label("Target Year:"),
        dcc.Slider(
            id="year",
            step=None,
            marks={year: str(year) for year in controls.get_years()},
        ),
    ],
)
requirements = html.Div(
    [
        html.Label("Requirements:"),
        dbc.RadioItems(
            id="requirements",
            options=[
                {"label": "Area", "value": "area"},
                {"label": "Water", "value": "water"},
            ],
            value="area",
        ),
    ],
)
unit = html.Div(
    [
        html.Label("Unit:"),
        dbc.RadioItems(
            id="unit",
            options=[
                {"label": "Percentage", "value": "percentage"},
                {"label": "Soccer Fields", "value": "soccer"},
            ],
            value="percentage",
        ),
    ],
)
criteria_options = controls.get_criteria()
criteria = html.Div(
    [
        html.Label("Criteria for requirements:"),
        dcc.Dropdown(
            options=criteria_options,
            value=criteria_options,
            multi=True,
        ),
    ],
)

region = html.Section(title="Region")
atlas = html.Section(title="Choropleth")
controls = html.Section(
    title="Settings",
    children=[scenario, year, requirements, unit, criteria],
)

DEFAULT_LAYOUT = dbc.Container(
    [dbc.Row([dbc.Col(region), dbc.Col(atlas), dbc.Col(controls)])],
)
