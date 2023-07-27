"""Holds functionality to read data."""
import json

import pandas as pd

import data
import settings

ONSHORE_GEOJSON_FILENAME = "regions_onshore_elec_s_30.geojson"
OFFSHORE_GEOJSON_FILENAME = "regions_offshore_elec_s_30.geojson"

SCENARIOS = ["clever", "tyndp_de"]


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

    df = df[df.target_year == year]
    df = df[df["type"].isin(criteria)]

    if requirement == "area":
        df = df.replace(
            {
                "H2 Electrolysis": "Electrolyser",
                "H2 Store": "H2 storage",
                "grid": "Grid",
                "offwind": "Offshore wind",
                "onwind": "Onshore wind",
                "solar": "PV",
                "solar rooftop": "PV rooftop",
            },
        )
    else:
        df = df.replace(
            {
                "H2 Electrolysis": "Electrolyser",
                "CCGT": "Gas",
                "OCGT": "Gas",
                "ror": "Hydro",
                "coal": "Coal",
                "lignite": "Lignite",
                "nuclear": "Nuclear",
                "oil": "Oil",
            },
        )
    df = df.rename(columns={"bus": "name"})
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
    return dataset["type"].unique().tolist()


def get_regions() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / ONSHORE_GEOJSON_FILENAME).open(
        "r",
        encoding="utf-8",
    ) as geojsonfile:
        return json.load(geojsonfile)


def get_regions_offshore() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / OFFSHORE_GEOJSON_FILENAME).open(
        "r",
        encoding="utf-8",
    ) as geojsonfile:
        return json.load(geojsonfile)


def get_min_max(req: str) -> (pd.DataFrame, pd.DataFrame):
    """Get min and max values for each unit of area requirement."""
    data_dict = {}
    if req == "area":
        for scenario in SCENARIOS:
            data_dict[scenario] = data.get_area_requirements(scenario)
        data_df = pd.concat(data_dict)[["area_km2", "oly_field", "rel"]].reset_index(
            drop=True,
        )
    elif req == "water":
        for scenario in SCENARIOS:
            data_dict[scenario] = data.get_water_requirements(scenario)
        data_df = pd.concat(data_dict)[["water_miom3", "oly_pool"]].reset_index(
            drop=True,
        )
    else:
        msg = "Invalid requirement. Call for either 'area' or 'water'."

        class ExceptionReqError(Exception):
            pass

        raise ExceptionReqError(msg)

    min_vals = data_df.min()
    max_vals = data_df.max()

    return min_vals, max_vals
