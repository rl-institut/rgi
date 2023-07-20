"""Module holds dash app, urls and views."""

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly import express as px

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
        Output(component_id="choropleth", component_property="figure"),
    ],
    [
        Input(component_id="year", component_property="value"),
        Input(component_id="requirement", component_property="value"),
    ],
)
def choropleth(year: int, requirement: str) -> tuple[px.choropleth]:
    """Return choropleth for given user settings."""
    return (graphs.get_choropleth(requirement=requirement, year=year),)


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=True,
        use_reloader=True,
        passthrough_errors=True,
    )
