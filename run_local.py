import warnings

import dotenv

found_env = dotenv.load_dotenv(".envs/.local/.env")
if not found_env:
    warnings.warn("Could not find local env file.")

import settings  # noqa: E402
from app import app  # noqa: E402

app.run_server(
    debug=settings.DEBUG,
    use_debugger=True,
    use_reloader=True,
    passthrough_errors=True,
)
