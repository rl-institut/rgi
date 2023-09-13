"""Module holds dash app, urls and views."""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, ctx, callback
from plotly import graph_objects as go

import data
import graphs
import layout
import settings
from flask_caching import Cache

config = {'responsive': True}
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
                {"label": "km²", "value": "area_km2"},
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
        Input(component_id="spatial_res", component_property="value"),
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
        spatial_res: str,
        requirement: str,
        unit: str,
        criteria: list[str],
) -> tuple[go.Figure, go.Figure, str, str]:
    """Return choropleth for given user settings."""
    if scenarios == "scenario_single":
        return (
            graphs.get_choropleth(
                scenario=scenario,
                spatial_res=spatial_res,
                requirement=requirement,
                year=year,
                unit=unit,
                criteria=criteria,
                min_max=get_min_max(requirement, criteria, scenarios, year, scenario, spatial_res=spatial_res),
                height=800, scenarios=scenarios, coloraxes=True
            ),
            graphs.blank_fig(),
            "col-11",
            "col-1",
        )
    return (
        graphs.get_choropleth(
            scenario=scenario_1,
            spatial_res=spatial_res,
            requirement=requirement,
            year=year,
            unit=unit,
            criteria=criteria,
            min_max=get_min_max(requirement, criteria, scenarios, year,
                                scenario_1=scenario_1, scenario_2=scenario_2, spatial_res=spatial_res),
            height=600, scenarios=scenarios, coloraxes=False
        ),
        graphs.get_choropleth(
            scenario=scenario_2,
            spatial_res=spatial_res,
            requirement=requirement,
            year=year,
            unit=unit,
            criteria=criteria,
            min_max=get_min_max(requirement, criteria, scenarios, year,
                                scenario_1=scenario_1, scenario_2=scenario_2, spatial_res=spatial_res),
            height=600, scenarios=scenarios, coloraxes=True
        ),
        "col-5",
        "col-6",
    )


@callback(
        Output('textarea-scenario', 'children'),
        [Input(component_id="scenarios", component_property="active_tab"),
         Input(component_id="scenario", component_property="value"),
         Input(component_id="scenario_1", component_property="value"),
         Input(component_id="scenario_2", component_property="value")]
)
def update_output(scenarios: str, scenario: str, scenario_1: str,
                  scenario_2: str,):
    if scenarios == "scenario_single":
        return layout.convert_to_markdown(data.get_scenario_text()[scenario])
    else:
        try:
            return layout.convert_to_markdown(data.get_scenario_text()[scenario_1]+"\n"+data.get_scenario_text()[scenario_2])
        except KeyError:
            pass


@callback(
    Output(component_id="scenario_1", component_property="value"),
    Output(component_id="scenario_2", component_property="value"),
    Input(component_id="scenario_1", component_property="value"),
    Input(component_id="scenario_2", component_property="value"),
)
def sync_input(sce1, sce2):
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if (sce1 == sce2) | ((sce1 == "clever")
                         & (sce2 == "CLEVER")) | ((sce2 == "clever")
                                                  & (sce1 == "CLEVER")):
        if input_id == "scenario_1":
            sce2 = [x for x in data.get_scenarios() if x != data.get_sce_names()[sce1]]
            sce2 = data.get_sce_pretty_names()[sce2[0]]
        else:
            sce1 = [x for x in data.get_scenarios() if x != data.get_sce_names()[sce2]]
            sce1 = data.get_sce_pretty_names()[sce1[0]]
    return sce1, sce2


@app.callback(
    Output(component_id="region_dd", component_property="value"),
    [
        Input(component_id="choropleth_1", component_property="clickData"),
        Input(component_id="choropleth_2", component_property="clickData"),
        Input(component_id="region_dd", component_property="value")
    ]
)
def update_region_dd(
        choropleth_feature_1: dict,
        choropleth_feature_2: dict,
        region: str):
    """Update region in drop down menu if region is selected on map."""
    choropleth_triggered = ctx.triggered_id
    if (choropleth_triggered == "choropleth_1") & (choropleth_feature_1 is not None):
        region = data.get_pretty_names()[choropleth_feature_1["points"][0]["location"]]
        if "," in region:
            region = "- "+region
        return region
    elif (choropleth_triggered == "choropleth_2") & (choropleth_feature_2 is not None):
        region = data.get_pretty_names()[choropleth_feature_2["points"][0]["location"]]
        if "," in region:
            region = "- " + region
        return region
    else:
        return region


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
        Input(component_id="region_dd", component_property="value"),
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
        region: str,
        criteria: list[str],
) -> tuple[go.Figure]:
    """Return bar chart for selected region."""
    choropleth_triggered = ctx.triggered_id
    if choropleth_triggered is None:
        return (graphs.blank_fig(),)
    if (choropleth_triggered in (
            "scenarios",
            "scenario",
            "scenario_1",
            "scenario_2",
            "requirement",
            "unit",
            "criteria",
            "year"
    )) & (choropleth_feature_1 is None) & (choropleth_feature_2 is None):
        if "- " in region:
            region = region[2:]
        name = [name for name, v in data.get_pretty_names().items() if v == region][0]
        region = name
    elif choropleth_triggered == "region_dd":
        if "- " in region:
            region = region[2:]
        name = [name for name, v in data.get_pretty_names().items() if v == region][0]
        region = name
    elif (choropleth_triggered == "choropleth_1") or ((choropleth_triggered == "year") & (choropleth_feature_1 is not None) & (region is None)):
        region = choropleth_feature_1["points"][0]["location"]
    elif (choropleth_triggered == "choropleth_2") or ((choropleth_triggered == "year") & (choropleth_feature_2 is not None) & (region is None)):
        region = choropleth_feature_2["points"][0]["location"]
    else:
        if region is not None:
            if "- " in region:
                region = region[2:]
            name = [name for name, v in data.get_pretty_names().items() if v == region][
                0]
            region = name
        else:
            return (graphs.blank_fig(),)

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
def get_min_max(req: str, criteria: [str], scenarios: str, year: int, scenario=None,
                scenario_1=None, scenario_2=None, spatial_res="region"
                ) -> tuple:
    """Get min and max values for each unit in tuple of pd.DataFrames."""
    min_df, max_df = data.get_min_max(req, criteria, spatial_res)
    sce_names = data.get_sce_names()
    if scenarios == "scenario_single":
        min_val = min_df.loc[min_df.sce_name == sce_names[scenario]]
        max_val = max_df.loc[max_df.sce_name == sce_names[scenario]]
    else:
        min_val = min_df.loc[(min_df.sce_name == sce_names[scenario_1]) |
                             (min_df.sce_name == sce_names[scenario_2])]
        max_val = max_df.loc[(max_df.sce_name == sce_names[scenario_1]) |
                             (max_df.sce_name == sce_names[scenario_2])]
    return min_val.drop(columns=["sce_name", "target_year"]).min(), \
        max_val.drop(columns=["sce_name", "target_year"]).max()


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=True,
        use_reloader=True,
        passthrough_errors=True,
    )
