"""Holds functionality for plotly graphs."""

from plotly import express as px
from plotly import graph_objects as go

import data
from data import get_regions


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

    df = (
        data.get_area_requirements(scenario)
        if requirement == "area"
        else data.get_water_requirements(scenario)
    )

    df = df[df.target_year == year]
    df = df[df["type"].isin(criteria)]

    if requirement == "area":
        df = df.replace(
            {"H2 Electrolysis": "electrolyser", "H2 Store": "hydrogen storage"},
        )
    else:
        df = df.replace(
            {
                "H2 Electrolysis": "electrolyser",
                "CCGT": "gas",
                "OCGT": "gas",
                "ror": "hydro",
            },
        )

    df = (
        df[["bus", "target_year", unit]]
        .groupby(["bus", "target_year"])
        .sum()
        .reset_index()
    )

    geo_on = get_regions()

    df = df.rename(columns={"bus": "name"})

    fig = px.choropleth(
        df,
        geojson=geo_on,
        locations="name",
        color=unit,
        scope="europe",
        featureidkey="properties.name",
    )

    fig.update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 0}, width=800, height=700)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title={"text": title, "automargin": True})
    return fig
