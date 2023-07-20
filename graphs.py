"""Holds functionality for plotly graphs."""

from plotly import express as px

import data
from data import get_regions


def get_choropleth(requirement: str, year: int) -> px.choropleth:
    """Return choropleth for given user settings."""
    title = f"choropleth_map_aggregated_{requirement}_requirements"

    df = (
        data.get_area_requirements()
        if requirement == "area"
        else data.get_water_requirements()
    )
    requirement_key = "area_km2" if requirement == "area" else "water_miom3"

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
        df = df.groupby(["sce_name", "target_year", "bus", "type"]).sum().reset_index()

    df = (
        df[["bus", "target_year", requirement_key]]
        .groupby(["bus", "target_year"])
        .sum()
        .reset_index()
    )

    geo_on = get_regions()

    df = df.rename(columns={"bus": "name"})

    fig = px.choropleth(
        df[df.target_year == year],
        geojson=geo_on,
        locations="name",
        color=requirement_key,
        scope="europe",
        featureidkey="properties.name",
    )

    fig.update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 0}, width=800, height=700)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title={"text": title, "automargin": True})
    return fig
