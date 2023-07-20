"""Holds functionality for plotly graphs."""

from plotly import express as px
from plotly import graph_objects as go

import data


def blank_fig() -> go.Figure:
    """Return empty figure."""
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


def get_choropleth(
    scenario: str,
    requirement: str,
    year: int,
    unit: str,
    criteria: list[str],
) -> px.choropleth:
    """Return choropleth for given user settings."""
    title = f"choropleth_map_aggregated_{requirement}_requirements"

    df = data.prepare_data(scenario, requirement, year, unit, criteria)

    geojson = data.get_regions()

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="name",
        color=unit,
        scope="europe",
        featureidkey="properties.name",
    )

    fig.update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 0}, width=800, height=700)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title={"text": title, "automargin": True})
    return fig
