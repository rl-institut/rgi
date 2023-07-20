"""Holds functionality to set up controls."""

import pandas as pd

import settings


def get_years() -> list[int]:
    """Return years from dataset."""
    areas = pd.read_csv(settings.DATA_DIR / "area_joined.csv")
    return areas["target_year"].unique().tolist()


def get_criteria() -> list[int]:
    """Return criteria from dataset."""
    areas = pd.read_csv(settings.DATA_DIR / "area_joined.csv")
    return areas["type"].unique().tolist()
