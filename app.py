"""Module holds dash app, urls and views."""

import dash
import dash_bootstrap_components as dbc

import layout
import settings

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=4.0"},
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.layout = layout.DEFAULT_LAYOUT
server = app.server
server.secret_key = settings.SECRET_KEY


if __name__ == "__main__":
    app.run_server(
        debug=settings.DEBUG,
        use_debugger=True,
        use_reloader=True,
        passthrough_errors=True,
    )
