"""Holds dash layout."""

import dash_bootstrap_components as dbc
from dash import dcc, html

import data

pretty_names = data.get_sce_pretty_names()
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
                    options=[pretty_names[x] for x in scenario_options],
                    value=[pretty_names[x] for x in scenario_options][0],
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
                            options=[pretty_names[x] for x in scenario_options],
                            value=[pretty_names[x] for x in scenario_options][0],
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Label("Scenario 2:"),
                        dcc.Dropdown(
                            id="scenario_2",
                            options=[pretty_names[x] for x in scenario_options],
                            value=[pretty_names[x] for x in scenario_options][1],
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


def convert_to_markdown(text: str) -> str:
    """Convert text to markdown."""
    markdown = ""
    lines = text.split("\n")

    for line in lines:
        if line.startswith("#"):
            level = line.count("#")
            markdown += f"{'#' * level} {line[level:].strip()}\n"
        elif line.startswith("* "):
            markdown += f"- {line[2:]}\n"
        elif line.startswith("1. "):
            markdown += f"1. {line[3:]}\n"
        elif line.startswith("> "):
            markdown += f"> {line[2:]}\n"
        else:
            markdown += line + "\n"

    return markdown


scenario_text = html.Div(
    [
        dcc.Markdown(
            id="textarea-scenario",
            children=convert_to_markdown(
                scenario_description[[pretty_names[x] for x in scenario_options][0]],
            ),
            link_target="_blank",
        ),
    ],
)

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
spatial_res = html.Div(
    [
        html.Label("Spatial Resolution:"),
        dbc.RadioItems(
            id="spatial_res",
            options=[
                {"label": "Region", "value": "region"},
                {"label": "Country", "value": "country"},
            ],
            value="region",
        ),
    ],
    style={"margin-bottom": "10px"},
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
            labelStyle={"display": "block"},
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
                dcc.Graph(id="choropleth_1", style={"width": "100%"}),
            ],
        ),
        dbc.Col(
            id="col_choropleth_2",
            children=[
                dcc.Graph(
                    id="choropleth_2",
                    style={"width": "100%"},
                    config={"displayModeBar": False},
                ),
            ],
        ),
    ],
)
controls = html.Section(
    title="Settings",
    children=[scenario, year, spatial_res, requirements, unit, criteria],
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
                dbc.Col(
                    controls,
                    className="col-3",
                    style={
                        "margin-left": "20px",
                        "margin-right": "50px",
                        "margin-top": "80px",
                        "margin-bottom": "30px",
                    },
                ),
            ],
        ),
        # row with bar chart
        dbc.Row(
            [
                dbc.Col(region, className="col-8"),
                dbc.Col(scenario_text, className="col-3",
                        style={"margin-left": "20px",}
                        ),
            ],
        ),
        # style={"margin-right": "50px"}),
    ],
    fluid=True,
)
