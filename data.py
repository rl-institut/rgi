"""Holds functionality to read data."""
import json

import pandas as pd

import settings

AREA_FILENAME = "area_joined.csv"
WATER_FILENAME = "water_joined.csv"
ONSHORE_GEOJSON_FILENAME = "regions_onshore_elec_s_77.geojson"


def get_area_requirements() -> pd.DataFrame:
    """Return area requirement data."""
    return pd.read_csv(settings.DATA_DIR / AREA_FILENAME)


def get_water_requirements() -> pd.DataFrame:
    """Return water requirement data."""
    return pd.read_csv(settings.DATA_DIR / WATER_FILENAME)


def get_scenarios() -> list[str]:
    """Return scenarios from dataset."""
    areas = get_area_requirements()
    return areas["sce_name"].unique().tolist()


def get_years() -> list[int]:
    """Return years from dataset."""
    areas = get_area_requirements()
    return areas["target_year"].unique().tolist()


def get_criteria() -> list[str]:
    """Return criteria from dataset."""
    areas = get_area_requirements()
    return areas["type"].unique().tolist()


def get_regions() -> dict:
    """Get onshore regions."""
    with (settings.DATA_DIR / ONSHORE_GEOJSON_FILENAME).open(
        "r",
        encoding="utf-8",
    ) as geojsonfile:
        return json.load(geojsonfile)
