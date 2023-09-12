"""Holds functionality to read data."""
import json

import pandas as pd

import data
import settings

COUNTRY_SHAPES = "regions_onshore_elec_s_30.geojson"
ONSHORE_GEOJSON_FILENAME = "regions_onshore_elec_s_50.geojson"
C_ONSHORE_GEOJSON_FILENAME = "countries_onshore_elec_s_50.geojson"
OFFSHORE_GEOJSON_FILENAME = "regions_offshore_elec_s_50.geojson"
C_OFFSHORE_GEOJSON_FILENAME = "countries_offshore_elec_s_50.geojson"

SCENARIOS = ["clever", "tyndp_de", "tyndp_ga", "pac2_0"]
sce_names = {"CLEVER": "clever", 'TYNDP "Distributed Energy" (DE)': "tyndp_de",
                'TYNDP "Global Ambition" (GA)': "tyndp_ga",  "PAC2.0": "pac2_0"}
sce_pretty_names = {"clever": "CLEVER", "tyndp_de": 'TYNDP "Distributed Energy" (DE)',
                "tyndp_ga": 'TYNDP "Global Ambition" (GA)', "pac2_0": "PAC2.0"}

tech_dict_area = {
    "H2 Electrolysis": "Electrolyser",
    "H2 Store": "H2 storage",
    "grid": "Grid",
    "offwind": "Offshore wind",
    "onwind": "Onshore wind",
    "solar": "PV",
    "solar rooftop": "PV rooftop",
    "protected area": "Nature-protected area",
    "urban area": "Urban & industrial area",
}
tech_dict_water = {
    "H2 Electrolysis": "H2 production",
    "SMR": "H2 production",
    "gas": "Gas",
    "CCGT": "Gas",
    "OCGT": "Gas",
    "hydro": "Hydro",
    "ror": "Hydro",
    "coal": "Hard coal",
    "lignite": "Lignite",
    "nuclear": "Nuclear",
    "oil": "Oil",
    "biomass": "Biomass",
}

round_dict_area = {
    "area_km2": 2,
    "oly_field": 1,
    "rel": 2,
}
round_dict_water = {
    "water_mio3": 1,
    "oly_pool": 1,
}

scenario_description = {
    "CLEVER": "#### CLEVER Scenario:\n CLEVER stands for Collaborative Low Energy Vision for the"
              " European Region and it was developed by négaWatt Association "
              "through a bottom-up approach with 25 different partners. It focuses on "
              "reaching 100% renewables and climate neutrality by 2050 through two "
              "principles: (1) of sufficiency (that redefines the needs for "
              "resource-intensive services) and (2) efficiency (that reduces the energy"
              " demand). You can find the CLEVER scenario [here](https://clever-energy-scenario.eu/). "
              "The underlying results for "
              "[water](https://github.com/rl-institut/rgi/blob/main/data/clever_water_joined.csv) "
              "and [area](https://github.com/rl-institut/rgi/blob/main/data/clever_area_joined.csv) "
              "requirements are available on Github.",
    "PAC2.0": "#### PAC2.0 Scenario:\nThe Paris Agreement Compatible (PAC) Scenario, was "
              "developed in 2020 by Climate Action Network (CAN) Europe and the "
              "European Environmental Bureau (EEB) under the banner "
              "[of the PAC project](https://www.pac-scenarios.eu/)."
              " It aims at achieving 100% renewables and net-zero greenhouse gas "
              "emissions by 2040 (with an intermediate step of 65% GHG emissions "
              "reduction by 2030), with emphasis on efficiency. 2022 datasets are used "
              "for this analysis and the updated in 2023 and nationally disaggregated "
              "scenarios can be found [here](https://www.pac-scenarios.eu/pac-scenario/how-a-europe-on-track-of-meeting-the-15c-would-look-like.html)."
              " The underlying results for "
              "[water](https://github.com/rl-institut/rgi/blob/main/data/pac2_0_water_joined.csv) "
              "and [area](https://github.com/rl-institut/rgi/blob/main/data/pac2_0_area_joined.csv) "
              "requirements are available on Github.",
    'TYNDP "Distributed Energy" (DE)': '#### TYNDP "Distributed Energy" (DE):\nDistributed Energy is one of the top-down '
                                       'scenarios developed by the European Network of '
                                       'Transmission System Operators for Electricity '
                                       '(ENTSO-E) together with the European Network of'
                                       ' Transmission System Operators for Gas (ENTSOG)'
                                       ' for the Ten-Year Network Development Plan '
                                       '(TYNDP). It assumes at least a 55% of GHG '
                                       'emission reduction in 2030 and climate '
                                       'neutrality in 2050. Its main drives are: '
                                       'reduced energy demand, transition initiated at '
                                       'local level and focus on decentralised '
                                       'technologies. More information can be found '
                                       '[here](https://2022.entsos-tyndp-scenarios.eu/wp-content/uploads/2022/04/TYNDP2022_Joint_Scenario_Full-Report-April-2022.pdf).'
                                       " The underlying results for "
                                       "[water](https://github.com/rl-institut/rgi/blob/main/data/tyndp_de_water_joined.csv) "
                                       "and [area](https://github.com/rl-institut/rgi/blob/main/data/tyndp_de_area_joined.csv) "
                                       "requirements are available on Github.",
    'TYNDP "Global Ambition" (GA)': '#### TYNDP "Global Ambition" (GA):\nGlobal Ambition is one of the top-down scenarios'
                                    ' developed by the European Network of Transmission'
                                    ' System Operators for Electricity (ENTSO-E) '
                                    'together with the European Network of Transmission'
                                    ' System Operators for Gas (ENTSOG) for the '
                                    'Ten-Year Network Development Plan (TYNDP). It '
                                    'assumes at least a 55% of GHG emission reduction '
                                    'in 2030 and aims at achieving climate neutrality '
                                    'by 2050. Its main drives are: large scale '
                                    'technologies, decarbonisation of energy supply, '
                                    'while including imports and low carbon energy '
                                    '(nuclear and integration of CCS). More information'
                                    ' can be found [here](https://2022.entsos-tyndp-scenarios.eu/wp-content/uploads/2022/04/TYNDP2022_Joint_Scenario_Full-Report-April-2022.pdf).'
                                    " The underlying results for "
                                    "[water](https://github.com/rl-institut/rgi/blob/main/data/tyndp_ga_water_joined.csv) "
                                    "and [area](https://github.com/rl-institut/rgi/blob/main/data/tyndp_ga_area_joined.csv) "
                                    "requirements are available on Github.",
}


def prepare_data(
    scenario: str,
    requirement: str,
    year: int,
    criteria: list[str],
) -> pd.Series:
    """Filter and aggregate data by given user settings."""
    df = (
        data.get_area_requirements(sce_names[scenario])
        if requirement == "area"
        else data.get_water_requirements(sce_names[scenario])
    )

    df = (
        df.replace(tech_dict_area)
        if requirement == "area"
        else df.replace(tech_dict_water)
    )

    df = df[df.target_year == year]
    df = df[df["type"].isin(criteria)]
    df = df.rename(columns={"bus": "name"})
    # round values
    df = (
        df.round(round_dict_area)
        if requirement == "area"
        else df.round(round_dict_water)
    )
    # only keep values with fields or pools >= 1
    df = (
        df.loc[df.oly_field >= 1] if requirement == "area" else df.loc[df.oly_pool >= 1]
    )

    return df


def get_area_requirements(scenario: str) -> pd.DataFrame:
    """Return area requirement data."""
    filename = f"{scenario}_area_joined.csv"
    return pd.read_csv(settings.DATA_DIR / filename)


def get_water_requirements(scenario: str) -> pd.DataFrame:
    """Return water requirement data."""
    filename = f"{scenario}_water_joined.csv"
    return pd.read_csv(settings.DATA_DIR / filename)


def get_pretty_names(offshore=False) -> dict:
    """Return pretty country names data."""
    filename = "pretty_names.csv"
    df = pd.read_csv(settings.DATA_DIR / filename)
    if offshore:
        df["pretty_name"] = [", ".join([df.country_name[i], df.Name[i], "Offshore "])
                             if df.boolean[i]
                             else ", ".join([df.country_name[i], "Offshore "])
                             for i in df.index]
    else:
        df["pretty_name"] = [", ".join([df.country_name[i], df.Name[i]])
                             if df.boolean[i]
                             else ", ".join([df.country_name[i]])
                             for i in df.index]
    return dict(zip(df.name, df.pretty_name))


def get_scenarios() -> list[str]:
    """Return scenarios from dataset."""
    return SCENARIOS


def get_sce_names() -> dict:
    """Return scenario dict from dataset."""
    return sce_names


def get_sce_pretty_names() -> dict:
    """Return scenario dict from dataset."""
    return sce_pretty_names


def get_scenario_text() -> dict:
    """Return scenario description from dataset."""
    return scenario_description


def get_years() -> list[int]:
    """Return years from dataset."""
    areas = get_area_requirements(SCENARIOS[0])
    return areas["target_year"].unique().tolist()


def get_criteria(requirement: str) -> list[str]:
    """Return criteria from dataset."""
    dataset = (
        get_area_requirements(SCENARIOS[0])
        if requirement == "area"
        else get_water_requirements(SCENARIOS[0])
    )

    dataset = (
        dataset.replace(tech_dict_area)
        if requirement == "area"
        else dataset.replace(tech_dict_water)
    )
    if requirement == "water":
        criteria = dataset["type"].sort_values().unique().tolist()
    else:
        criteria = dataset["type"].sort_values().unique().tolist()
        criteria.remove('Nature-protected area')
        criteria.insert(len(criteria)-1, 'Nature-protected area')
    return criteria


def get_regions(spatial_res) -> dict:
    """Get onshore regions."""
    if spatial_res == "region":
        with (settings.DATA_DIR / ONSHORE_GEOJSON_FILENAME).open(
                "r",
                encoding="utf-8",
        ) as geojsonfile:
            return json.load(geojsonfile)
    elif spatial_res == "country":
        with (settings.DATA_DIR / C_ONSHORE_GEOJSON_FILENAME).open(
                "r",
                encoding="utf-8",
        ) as geojsonfile:
            return json.load(geojsonfile)


def get_country_shapes() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / COUNTRY_SHAPES).open(
        "r",
        encoding="utf-8",
    ) as geojsonfile:
        return json.load(geojsonfile)


# function to get state boundaries from country shapes geojson
def state_boundaries(geojdata: object) -> tuple:
    """Extract longitudes and latitudes from geojson file."""
    # code from
    # https://community.plotly.com/t/in-choropleth-how-to-create-outline-for-country-and-differentiate-that-particular-countries-states/67013/4
    pts = (
        []
    )  # list of points defining boundaries of polygons, pts has as coordinates the lon and lat
    for feature in geojdata["features"]:
        if feature["geometry"]["type"] == "Polygon":
            pts.extend(feature["geometry"]["coordinates"][0])
            pts.append([None, None])  # mark the end of a polygon

        elif feature["geometry"]["type"] == "MultiPolygon":
            for polyg in feature["geometry"]["coordinates"]:
                pts.extend(polyg[0])
                pts.append([None, None])  # end of polygon
        elif feature["geometry"]["type"] == "LineString":
            pts.extend(feature["geometry"]["coordinates"])
            pts.append([None, None])
        else:
            pass
        # else: raise ValueError("geometry type irrelevant for map")
    lons, lats = zip(*pts)
    return lons, lats


def get_regions_offshore(spatial_res) -> dict:
    """Get offshore regions."""
    if spatial_res == "region":
        with (settings.DATA_DIR / OFFSHORE_GEOJSON_FILENAME).open(
                "r",
                encoding="utf-8",
        ) as geojsonfile:
            return json.load(geojsonfile)
    elif spatial_res == "country":
        with (settings.DATA_DIR / C_OFFSHORE_GEOJSON_FILENAME).open(
                "r",
                encoding="utf-8",
        ) as geojsonfile:
            return json.load(geojsonfile)


def get_min_max(req: str, criteria: list[str]) -> (pd.DataFrame, pd.DataFrame):
    """Get min and max values for each unit of area requirement."""
    data_dict = {}
    if req == "area":
        for scenario in SCENARIOS:
            df = data.get_area_requirements(scenario)
            df = df.replace(
                tech_dict_area,
            )
            data_dict[scenario] = df[(df["type"].isin(criteria)) & (df.onshore)]

        data_df = pd.concat(data_dict)
        # ToDo
        #  if len(region)>3 for regions, elif region == EU for EU, else for countries
        data_df = data_df.loc[[True if len(region) > 3
                               else False for region in data_df.bus]]
        data_df = (
            data_df.groupby(["bus", "target_year", "sce_name"])
            # differentiation possible for aggregation in case e.g. percentage needs to be averaged instead of summed
            .aggregate({"area_km2": "sum", "oly_field": "sum", "rel": "sum"})[
                ["area_km2", "oly_field", "rel"]
            ].reset_index()[["sce_name", "target_year", "area_km2", "oly_field", "rel"]]
        )
    elif req == "water":
        for scenario in SCENARIOS:
            df = data.get_water_requirements(scenario)
            df = df.replace(
                tech_dict_water,
            )
            data_dict[scenario] = df[(df["type"].isin(criteria)) & (df.onshore)]
        data_df = pd.concat(data_dict)
        # ToDo
        #  if len(region)>3 for regions, elif region == EU for EU, else for countries
        data_df = data_df.loc[[True if len(region) > 3
                               else False for region in data_df.bus]]
        data_df = (
            data_df.groupby(["bus", "target_year", "sce_name"])
            .sum()[["water_miom3", "oly_pool"]]
            .reset_index()[["sce_name", "target_year", "water_miom3", "oly_pool"]]
        )
    else:
        msg = "Invalid requirement. Call for either 'area' or 'water'."

        class ExceptionReqError(Exception):
            pass

        raise ExceptionReqError(msg)

    min_vals = data_df.groupby(by=["sce_name", "target_year"]).min().reset_index()
    max_vals = data_df.groupby(by=["sce_name", "target_year"]).max().reset_index()
    return min_vals, max_vals
