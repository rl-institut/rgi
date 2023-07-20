"""Holds settings for dash app."""

import os
import warnings

VERSION = "0.16.0"

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    warnings.warn(
        "No secret key found - never run in production mode without a secret key!",
        stacklevel=2,
    )
DEBUG = os.environ.get("DEBUG", "False") == "True"
