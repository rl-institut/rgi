"""Module holds dash app, urls and views."""

import pathlib

import dash
import dash_bootstrap_components as dbc

import settings

APP_PATH = str(pathlib.Path(__file__).parent.resolve())


app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=4.0"},
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server
server.secret_key = settings.SECRET_KEY


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=False,
        use_reloader=False,
        passthrough_errors=True,
    )
