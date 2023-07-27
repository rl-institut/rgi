"""Holds functionality for plotly graphs."""
import numpy as np
import pandas as pd
from plotly import express as px
from plotly import graph_objects as go

import data

# add font variable to adjust graph font
FONT = "Lato"

# pretty labels for pretty plotting
pretty_labels = {
    "area_km2": "Area [km2]",
    "oly_field": "Area [Olympic soccer fields]",
    "rel": "Area [%]",
    "water_miom3": "Water [Mio. m³]",
    "oly_pool": "Water [Olympic swimming pools]",
    "type": "Technology type",
    "target_year": "Year",
    "sce_name": "Scenario",
    "electrolyser": "Electrolyser",
    "hydrogen storage": "H2 Storage",
    "clever": "CLEVER",
    "tyndp_de": "TYNDP_de"
}

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
    min_max: tuple[pd.DataFrame, pd.DataFrame]
) -> px.choropleth:
    """Return choropleth for given user settings."""

    title = f"{pretty_labels[scenario]} spatial {requirement} requirement for {year}"

    df = data.prepare_data(
        scenario=scenario,
        requirement=requirement,
        year=year,
        criteria=criteria,
    )
    if unit == "rel":
        df = (
            df[["name", "target_year", unit]]
            .groupby(["name", "target_year"])
            .mean()
            .reset_index()
        )
    else:
        df = (
            df[["name", "target_year", unit]]
            .groupby(["name", "target_year"])
            .sum()
            .reset_index()
        )

    # add pretty name for hovering box
    df["pretty_name"] = df.name.str[:5]
    df["offshore_color"] = np.repeat("offshore", len(df))

    geojson = data.get_regions()
    geojson_offshore = data.get_regions_offshore()

    # add color scale
    if requirement == "area":
        scale = [(0, "#c3ddd2"), (0.33, "#82af9c"), (0.66, "#557c69"), (1, "#31493e")]
    else:
        scale = [(0, "#d0edf4"), (0.33, "#8cd0d3"), (0.66, "#5091a0"), (1, "#2e5460")]

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="name",
        color=unit,
        color_continuous_scale=scale,
        scope="europe",
        featureidkey="properties.name",
        hover_name="pretty_name",
        hover_data={"name": False, unit: True},
        labels=pretty_labels,
        range_color=(min_max[0][unit], min_max[1][unit]),
    )

    fig2 = px.choropleth(
        df,
        geojson=geojson_offshore,
        locations='name',
        color="offshore_color",
        color_discrete_map={
            'offshore': '#8AC7DB'},
        # opacity=0.1,
        featureidkey="properties.name",
        hover_name=df.pretty_name + " Offshore",
        hover_data={"name": False, unit: False, "offshore_color": False},
        labels=pretty_labels,
    )

    if len(criteria) > 0:
        fig.add_trace(fig2.data[0])

    fig.update_layout(
        showlegend=False,
        margin={"l": 0, "r": 0, "b": 0, "t": 75},
        font_family=FONT,
        title={"text": title},
        hoverlabel={"bgcolor": "white", "font_size": 12, "font_family": FONT}
    )

    fig.update_geos(
        scope="europe",
        fitbounds="locations",
        visible=False,
        resolution=50,
        showcoastlines=True, coastlinecolor="lightgrey",
        showocean=True, oceancolor="LightBlue"
    )

    # fig.layout.coloraxis.colorbar.title = pretty_labels[unit]

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
    # title = f"{requirement.capitalize()} requirement by technology type"

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

    # add color palette for bar chart
    if requirement == "area":
        bar_palette = {
            "Onshore wind": "#d0edf4",
            "Offshore wind": "#0FB3CE",
            "PV": "#FFB703",
            "PV rooftop": "#DA7635",
            "H2 storage": "#b09ac1",
            "Electrolyser": "#7d5ba6",
            "Grid": "#9bb765",
            "nature-protected areas": "#627732",
            "cities&industry": "#adadad"
        }
    else:
        bar_palette = {
            "Hydro": "#d0edf4",
            "Nuclear": "#5091a0",
            "Oil": "#f9dbbd",
            "Gas": "#9B2226",
            "Lignite": "#adadad",
            "Coal": "#4c4c4c",
            "Electrolyser": "#7d5ba6",
        }

    fig = px.bar(
        df,
        x="target_year",
        y=unit,
        facet_col="sce_name",
        barmode="group",
        color="type",
        color_discrete_map=bar_palette,
        hover_name="type",
        hover_data={"name": False, "type":False, unit: True},
        labels=pretty_labels
    )
    fig.for_each_annotation(lambda a: a.update(text=""))

    fig.update_layout(
        # title={"text": title},
        font_family=FONT,
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=75),
        legend=dict(
            traceorder="reversed",
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        hoverlabel={"bgcolor": "white", "font_size": 12, "font_family": FONT}
    )

    fig.update_yaxes(
        ticks='outside',
        showline=False,
        linecolor='lightgrey',
        gridcolor='lightgrey'
    )

    fig.update_xaxes(
        linecolor='lightgrey'
    )

    return fig
