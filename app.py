"""Module holds dash app, urls and views."""

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
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
    criteria: list[str],
) -> tuple[go.Figure, go.Figure]:
    """Return choropleth for given user settings."""
    if scenarios == "scenario_single":
        return (
            graphs.get_choropleth(
                scenario=scenario,
                requirement=requirement,
                year=year,
                criteria=criteria,
            ),
            graphs.blank_fig(),
        )
    return graphs.get_choropleth(
        scenario=scenario_1,
        requirement=requirement,
        year=year,
        criteria=criteria,
    ), graphs.get_choropleth(
        scenario=scenario_2,
        requirement=requirement,
        year=year,
        criteria=criteria,
    )


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=True,
        use_reloader=True,
        passthrough_errors=True,
    )
