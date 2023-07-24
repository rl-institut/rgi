"""Holds functionality for plotly graphs."""

import pandas as pd
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

    df = data.prepare_data(
        scenario=scenario,
        requirement=requirement,
        year=year,
        criteria=criteria,
    )
    df = (
        df[["name", "target_year", unit]]
        .groupby(["name", "target_year"])
        .sum()
        .reset_index()
    )

    geojson = data.get_regions()

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="name",
        color=unit,
        scope="europe",
        featureidkey="properties.name",
    )

    fig.update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 0})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title={"text": title, "automargin": True})
    return fig


def get_bar_chart(  # noqa: PLR0913
    scenarios: list[str],
    requirement: str,
    year: int,
    unit: str,
    criteria: list[str],
    region: str,
) -> go.Figure:
    """Return bar chart for selected region."""
    title = f"bar_chart_{requirement}_requirement_per_year"

    df = pd.concat(
        data.prepare_data(
            scenario=scenario,
            requirement=requirement,
            year=year,
            criteria=criteria,
        )
        for scenario in scenarios
    )
    df = df[df["name"] == region]

    fig = px.bar(
        df,
        x="target_year",
        y=unit,
        facet_col="sce_name",
        barmode="group",
        color="type",
    )
    fig.update_layout(title={"text": title, "automargin": True})
    return fig
