"""Module holds dash app, urls and views."""

import pathlib

import dash
import dash_bootstrap_components as dbc

import settings

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

# Initialize app
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=4.0"},
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

server = app.server
server.secret_key = settings.SECRET_KEY
