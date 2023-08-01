"""Holds functionality to read data."""
import json

import pandas as pd

import data
import settings

COUNTRY_SHAPES = "regions_onshore_elec_s_30.geojson"
ONSHORE_GEOJSON_FILENAME = "regions_onshore_elec_s_50.geojson"
OFFSHORE_GEOJSON_FILENAME = "regions_offshore_elec_s_50.geojson"

SCENARIOS = ["clever", "tyndp_de", "tyndp_ga", "pac2_0"]

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


def prepare_data(
    scenario: str,
    requirement: str,
    year: int,
    criteria: list[str],
) -> pd.Series:
    """Filter and aggregate data by given user settings."""
    df = (
        data.get_area_requirements(scenario)
        if requirement == "area"
        else data.get_water_requirements(scenario)
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


def get_scenarios() -> list[str]:
    """Return scenarios from dataset."""
    return SCENARIOS


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

    return dataset["type"].unique().tolist()


def get_regions() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / ONSHORE_GEOJSON_FILENAME).open(
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


def get_regions_offshore() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / OFFSHORE_GEOJSON_FILENAME).open(
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
        data_df = (
            data_df.groupby(["bus", "target_year", "sce_name"])
            # differentiation possible for aggregation in case e.g. percentage needs to be averaged instead of summed
            .aggregate({"area_km2": "sum", "oly_field": "sum", "rel": "sum"})[
                ["area_km2", "oly_field", "rel"]
            ].reset_index(drop=True)
        )
    elif req == "water":
        for scenario in SCENARIOS:
            df = data.get_water_requirements(scenario)
            df = df.replace(
                tech_dict_water,
            )
            data_dict[scenario] = df[(df["type"].isin(criteria)) & (df.onshore)]
        data_df = pd.concat(data_dict)
        data_df = (
            data_df.groupby(["bus", "target_year", "sce_name"])
            .sum()[["water_miom3", "oly_pool"]]
            .reset_index(drop=True)
        )
    else:
        msg = "Invalid requirement. Call for either 'area' or 'water'."

        class ExceptionReqError(Exception):
            pass

        raise ExceptionReqError(msg)

    min_vals = data_df.min()
    max_vals = data_df.max()

    return min_vals, max_vals
