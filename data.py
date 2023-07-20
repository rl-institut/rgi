"""Holds functionality to read data."""
import json

import pandas as pd

import settings

ONSHORE_GEOJSON_FILENAME = "regions_onshore_elec_s_77.geojson"

SCENARIOS = ["clever", "tyndp_de"]


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


def get_criteria() -> list[str]:
    """Return criteria from dataset."""
    areas = get_area_requirements(SCENARIOS[0])
    return areas["type"].unique().tolist()


def get_regions() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / ONSHORE_GEOJSON_FILENAME).open(
        "r",
        encoding="utf-8",
    ) as geojsonfile:
        return json.load(geojsonfile)
