"""Module holds dash app, urls and views."""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, ctx
from plotly import graph_objects as go

import data
import graphs
import layout
import settings
from flask_caching import Cache

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=4.0"},
    ],
    external_stylesheets=["assets/custom.css", dbc.themes.BOOTSTRAP],
)
app.layout = layout.DEFAULT_LAYOUT
server = app.server
server.secret_key = settings.SECRET_KEY

cache = Cache(
    app.server,
    config={
        # try 'filesystem' if you don't want to setup redis
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
    },
)


@app.callback(
    [
        Output(component_id="unit", component_property="options"),
        Output(component_id="unit", component_property="value"),
        Output(component_id="criteria", component_property="options"),
        Output(component_id="criteria", component_property="value"),
    ],
    Input(component_id="requirement", component_property="value"),
    prevent_initial_call=True,
)
def change_unit(
    requirement: str,
) -> tuple[list[dict[str, str]], str, list[dict[str, str]], list[str]]:
    """Change unit related to selected requirement."""
    criteria = data.get_criteria(requirement)
    if requirement == "area":
        return (
            [
                {"label": "km²", "value": "area_km²"},
                {"label": "Percentage", "value": "rel"},
                {"label": "Olympic Soccer Fields (105 x 68 m²)", "value": "oly_field"},
            ],
            "rel",
            [{"label": option, "value": option} for option in criteria],
            criteria,
        )
    return (
        [
            {"label": "Mio. m³", "value": "water_miom3"},
            {"label": "Olympic Swimming Pools (50 x 25 x 2 m³)", "value": "oly_pool"},
        ],
        "water_miom3",
        [{"label": option, "value": option} for option in criteria],
        criteria,
    )


@app.callback(
    [
        Output(component_id="choropleth_1", component_property="figure"),
        Output(component_id="choropleth_2", component_property="figure"),
        Output(component_id="col_choropleth_1", component_property="className"),
        Output(component_id="col_choropleth_2", component_property="className"),
    ],
    [
        Input(component_id="scenarios", component_property="active_tab"),
        Input(component_id="scenario", component_property="value"),
        Input(component_id="scenario_1", component_property="value"),
        Input(component_id="scenario_2", component_property="value"),
        Input(component_id="year", component_property="value"),
        Input(component_id="requirement", component_property="value"),
        Input(component_id="unit", component_property="value"),
        Input(component_id="criteria", component_property="value"),
    ],
)
def choropleth(  # noqa: PLR0913
    scenarios: str,
    scenario: str,
    scenario_1: str,
    scenario_2: str,
    year: int,
    requirement: str,
    unit: str,
    criteria: list[str],
) -> tuple[go.Figure, go.Figure, str, str]:
    """Return choropleth for given user settings."""
    if scenarios == "scenario_single":
        return (
            graphs.get_choropleth(
                scenario=scenario,
                requirement=requirement,
                year=year,
                unit=unit,
                criteria=criteria,
                min_max=get_min_max(requirement, criteria),
            ),
            graphs.blank_fig(),
            "col-11",
            "col-1",
        )
    return (
        graphs.get_choropleth(
            scenario=scenario_1,
            requirement=requirement,
            year=year,
            unit=unit,
            criteria=criteria,
            min_max=get_min_max(requirement, criteria),
        ),
        graphs.get_choropleth(
            scenario=scenario_2,
            requirement=requirement,
            year=year,
            unit=unit,
            criteria=criteria,
            min_max=get_min_max(requirement, criteria),
        ),
        "col-6",
        "col-6",
    )


@app.callback(
    [
        Output(component_id="region", component_property="figure"),
    ],
    [
        Input(component_id="choropleth_1", component_property="clickData"),
        Input(component_id="choropleth_2", component_property="clickData"),
        Input(component_id="scenarios", component_property="active_tab"),
        Input(component_id="scenario", component_property="value"),
        Input(component_id="scenario_1", component_property="value"),
        Input(component_id="scenario_2", component_property="value"),
        Input(component_id="year", component_property="value"),
        Input(component_id="requirement", component_property="value"),
        Input(component_id="unit", component_property="value"),
        Input(component_id="criteria", component_property="value"),
    ],
)
def bar_chart(  # noqa: PLR0913
    choropleth_feature_1: dict,
    choropleth_feature_2: dict,
    scenarios: str,
    scenario: str,
    scenario_1: str,
    scenario_2: str,
    year: int,
    requirement: str,
    unit: str,
    criteria: list[str],
) -> tuple[go.Figure]:
    """Return bar chart for selected region."""
    choropleth_triggered = ctx.triggered_id
    if choropleth_triggered is None or choropleth_triggered in (
        "scenarios",
        "scenario",
        "scenario_1",
        "scenario_2",
        "year",
        "requirement",
        "unit",
        "criteria",
    ):
        return (graphs.blank_fig(),)
    if choropleth_triggered == "choropleth_1":
        region = choropleth_feature_1["points"][0]["location"]
    else:
        region = choropleth_feature_2["points"][0]["location"]

    region_scenarios = (
        [scenario] if scenarios == "scenario_single" else [scenario_1, scenario_2]
    )

    return (
        graphs.get_bar_chart(
            scenarios=region_scenarios,
            requirement=requirement,
            year=year,
            unit=unit,
            criteria=criteria,
            region=region,
        ),
    )


# @cache.memoize(timeout=0)
def get_min_max(req: str, criteria: [str]) -> tuple:
    """Get min and max values for each unit in tuple of pd.DataFrames."""
    return data.get_min_max(req, criteria)


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=True,
        use_reloader=True,
        passthrough_errors=True,
    )
