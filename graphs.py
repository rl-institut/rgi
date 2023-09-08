"""Holds functionality for plotly graphs."""
import numpy as np
import pandas as pd
from plotly import express as px
from plotly import graph_objects as go

import data

# add font variable to adjust graph font
FONT = "Lato"
FONT_COLOR = "#1f2120"

# pretty labels for pretty plotting
pretty_labels = {
    "area_km2": "Area (in km²)",
    "oly_field": "Area (in Soccer Fields)",
    "rel": "Area (in %)",
    "water_miom3": "Water (in Mio. m³)",
    "oly_pool": "Water (in Swimming pools)",
    "type": "Criteria for requirements",
    "target_year": "Year",
    "sce_name": "Scenario",
    "electrolyser": "Electrolyser",
    "hydrogen storage": "H2 Storage",
    "clever": "CLEVER",
    "tyndp_de": "TYNDP DE",
    "tyndp_ga": "TYNDP GA",
    "pac2_0": "PAC2.0",
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
        min_max: tuple[pd.DataFrame, pd.DataFrame],
        width: int,
        height: int,
        scenarios: str,
        coloraxes: bool
) -> px.choropleth:
    """Return choropleth for given user settings."""
    title = f"{pretty_labels[data.get_sce_names()[scenario]]} spatial {requirement} requirement for {year}"

    df = data.prepare_data(
        scenario=scenario,
        requirement=requirement,
        year=year,
        criteria=criteria,
    )

    df_offshore_all = df[~df.onshore][["name", "type", "target_year", unit]]

    df_offshore = pd.pivot_table(
        df_offshore_all,
        values=unit,
        index=["name", "target_year"],
        columns=["type"],
        aggfunc=np.sum,
    ).reset_index().fillna(0)

    df = (
        df[df.onshore][["name", "target_year", unit]]
        .groupby(["name", "target_year"])
        .sum()
        .reset_index()
    )

    # add pretty name for hovering box
    df["pretty_name"] = df["name"].replace(data.get_pretty_names())
    df_offshore["pretty_name"] = df_offshore["name"].replace(data.get_pretty_names(True))
    df_offshore["offshore_color"] = np.repeat("offshore", len(df_offshore))

    geojson = data.get_regions()
    geojson_offshore = data.get_regions_offshore()
    geojson_country_shapes = data.get_country_shapes()
    lons, lats = data.state_boundaries(geojson_country_shapes)

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
        hover_name=df.pretty_name+" <br> <i>Click to show bar plot with more detailed information below.</i>",
        hover_data={"name": False, unit: True},
        labels=pretty_labels,
        range_color=(min_max[0][unit], min_max[1][unit]),
        width=width, height=height
    )

    hover_dict = {"name": False, "offshore_color": False}

    if "Offshore wind" in criteria:
        if unit == "rel":
            hover_dict["Offshore wind area (in %)"] = True
            df_offshore.rename(columns={"Offshore wind": "Offshore wind area (in %)"}, inplace=True)
        elif unit == "area_km2":
            hover_dict["Offshore wind area (in km²)"] = True
            df_offshore.rename(columns={"Offshore wind": "Offshore wind area (in km²)"},
                               inplace=True)
        elif unit == "oly_field":
            hover_dict["Offshore wind area (in Soccer Fields)"] = True
            df_offshore.rename(columns={"Offshore wind": "Offshore wind area (in Soccer Fields)"},
                               inplace=True)
    if "Nature-protected area" in criteria:
        if unit == "rel":
            hover_dict["Nature-protected area (in %)"] = True
            df_offshore.rename(columns={"Nature-protected area": "Nature-protected area (in %)"}, inplace=True)
        elif unit == "area_km2":
            hover_dict["Nature-protected area (in km²)"] = True
            df_offshore.rename(columns={"Nature-protected area": "Nature-protected area (in km²)"},
                               inplace=True)
        elif unit == "oly_field":
            hover_dict["Nature-protected area (in Soccer Fields)"] = True
            df_offshore.rename(columns={"Nature-protected area": "Nature-protected area (in Soccer Fields)"},
                               inplace=True)

    # for offshore regions
    fig2 = px.choropleth(
        df_offshore,
        geojson=geojson_offshore,
        locations="name",
        color="offshore_color",
        color_discrete_map={
            "offshore": "white",
        },  # #8AC7DB as alternative blue offshore color
        featureidkey="properties.name",
        hover_name=df_offshore.pretty_name + ":<br> <i>Click to show bar plot with more detailed information below.</i>",
        hover_data=hover_dict,
        labels=pretty_labels,
        width=width, height=height
    )

    # for country borders
    fig3 = go.Figure(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="lines",
            line_width=1.5,
            line_color="#1f2120",  # can also set this to white or other if country borders should be different
            hoverinfo="skip",
        ),
    )

    if len(criteria) > 0:
        # add offshore regions traces
        if (requirement == "area") & (~df_offshore.empty):
            fig.add_trace(fig2.data[0])
        # add country border traces
        fig.add_trace(fig3.data[0])

    fig.update_layout(
        showlegend=False,
        margin={"l": 2, "r": 2, "b": 2, "t": 75},
        font_family=FONT,
        font_color=FONT_COLOR,
        title={"text": title},
        hoverlabel={
            "bgcolor": "white",
            "font_size": 12,
            "font_family": FONT,
            "font_color": FONT_COLOR,
        },
        # adapt color bar
        coloraxis_colorbar={
            "orientation": "v",
        },
    )

    if scenarios == "scenario_single":
        fig.update_coloraxes(colorbar_x=0.89)
    elif not coloraxes:
        fig.update(layout_coloraxis_showscale=False)

    fig.update_geos(
        scope="europe",
        fitbounds="locations",
        visible=False,
        resolution=50,
        showland=True,
        landcolor="lightgrey",
        # change background color of map
        bgcolor="#f5f7f7",
    )

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
    df = pd.concat(
        data.prepare_data(
            scenario=scenario,
            requirement=requirement,
            year=year,
            criteria=criteria,
        )
        for scenario in scenarios
    )
    df = df[(df["name"] == region) & (df.onshore)]

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
            "Nature-protected area": "#627732",
            "Urban & industrial area": "#adadad",
        }
        df = df.groupby(["sce_name", "type", 'target_year', 'name']).agg(
            {'area_km2': 'sum', 'oly_field': 'sum', 'rel': 'sum'}).reset_index()
    else:
        bar_palette = {
            "Biomass": "#a57f60",
            "Hydro": "#d0edf4",
            "Nuclear": "#5091a0",
            "Oil": "#f9dbbd",
            "Gas": "#9B2226",
            "Lignite": "#adadad",
            "Hard coal": "#4c4c4c",
            "H2 production": "#7d5ba6",
        }
        df = df.groupby(["sce_name", "type", 'target_year', 'name']).agg(
            {'oly_pool': 'sum', 'water_miom3': 'sum'}).reset_index()

    fig = px.bar(
        df,
        x="target_year",
        y=unit,
        facet_col="sce_name",
        barmode="group",
        color="type",
        color_discrete_map=bar_palette,
        hover_name="type",
        hover_data={"name": False, "sce_name": False, "type": False, unit: True},
        labels=pretty_labels,
    )

    # change annotation above graph to only show scenario name; optional: give text="" for no annotation
    fig.for_each_annotation(lambda a:
                            a.update(
                                text=f"{data.get_sce_pretty_names()[a.text[9:]]}:"
                                     f" {data.get_pretty_names()[region]}"))
    fig.update_annotations(font_size=18)
    # set fixed bar width
    fig.update_traces(width=0.08)

    fig.update_layout(
        font_family=FONT,
        font_color=FONT_COLOR,
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"t": 75},
        legend={
            "traceorder": "reversed",
            "bgcolor": "#f5f7f7",
            "bordercolor": "#1f2120",
            "borderwidth": 2,
        },
        hoverlabel={
            "bgcolor": "white",
            "font_size": 12,
            "font_family": FONT,
            "font_color": FONT_COLOR,
        },
    )

    fig.update_yaxes(
        ticks="outside",
        showline=False,
        linecolor="lightgrey",
        gridcolor="lightgrey",
    )

    fig.update_xaxes(
        tickvals=[year],
        linecolor="lightgrey"
    )

    return fig
