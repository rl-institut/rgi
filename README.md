# RGI

## Usage (production)

- create .env file in `.envs/.production/` folder
- `docker-compose -f production.yml up -d --build`
- point proxy server to docker container

## Usage (local)

- Create virtual environment: `python -m venv .venv`
- Activate environment: `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`
- Start application: `python run_local.py`
- Visit application in browser at http://127.0.0.1:8050/
