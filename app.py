"""Module holds dash app, urls and views."""

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from plotly import graph_objects as go

import graphs
import layout
import settings

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=4.0"},
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.layout = layout.DEFAULT_LAYOUT
server = app.server
server.secret_key = settings.SECRET_KEY


@app.callback(
    [
        Output(component_id="unit", component_property="options"),
        Output(component_id="unit", component_property="value"),
    ],
    Input(component_id="requirement", component_property="value"),
    prevent_initial_call=True,
)
def change_unit(requirement: str) -> tuple[list[dict[str, str]], str]:
    """Change unit related to selected requirement."""
    if requirement == "area":
        return [
            {"label": "Percentage", "value": "rel"},
            {"label": "Olympic Soccer Fields", "value": "oly_field"},
        ], "rel"
    return [
        {"label": "Mio. m³", "value": "water_miom3"},
        {"label": "Olympic Swimming Pools", "value": "oly_pool"},
    ], "water_miom3"


@app.callback(
    [
        Output(component_id="choropleth_1", component_property="figure"),
        Output(component_id="choropleth_2", component_property="figure"),
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
) -> tuple[go.Figure, go.Figure]:
    """Return choropleth for given user settings."""
    if scenarios == "scenario_single":
        return (
            graphs.get_choropleth(
                scenario=scenario,
                requirement=requirement,
                year=year,
                unit=unit,
                criteria=criteria,
            ),
            graphs.blank_fig(),
        )
    return graphs.get_choropleth(
        scenario=scenario_1,
        requirement=requirement,
        year=year,
        unit=unit,
        criteria=criteria,
    ), graphs.get_choropleth(
        scenario=scenario_2,
        requirement=requirement,
        year=year,
        unit=unit,
        criteria=criteria,
    )


@app.callback(
    [
        Output(component_id="region", component_property="figure"),
    ],
    [
        Input(component_id="choropleth_1", component_property="clickData"),
    ],
    [
        State(component_id="scenarios", component_property="active_tab"),
        State(component_id="scenario", component_property="value"),
        State(component_id="scenario_1", component_property="value"),
        State(component_id="scenario_2", component_property="value"),
        State(component_id="year", component_property="value"),
        State(component_id="requirement", component_property="value"),
        State(component_id="unit", component_property="value"),
        State(component_id="criteria", component_property="value"),
    ],
    prevent_initial_call=True,
)
def bar_chart(  # noqa: PLR0913
    choropleth_feature: dict,
    scenarios: str,  # noqa: ARG001
    scenario: str,
    scenario_1: str,  # noqa: ARG001
    scenario_2: str,  # noqa: ARG001
    year: int,
    requirement: str,
    unit: str,
    criteria: list[str],
) -> tuple[go.Figure]:
    """Return bar chart for selected region."""
    region = choropleth_feature["points"][0]["location"]

    # TODO (Hendrik): Implement scenario selection (single/comparison)
    # https://github.com/rl-institut/rgi/issues/1
    return (
        graphs.get_bar_chart(
            scenario=scenario,
            requirement=requirement,
            year=year,
            unit=unit,
            criteria=criteria,
            region=region,
        ),
    )


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=True,
        use_reloader=True,
        passthrough_errors=True,
    )
