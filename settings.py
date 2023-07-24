"""Holds settings for dash app."""

import os
import pathlib

VERSION = "0.2.0"

DEBUG = os.environ.get("DEBUG", "False") == "True"
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    msg = "No secret key found"
    raise RuntimeError(msg)

ROOT_DIR = pathlib.Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
