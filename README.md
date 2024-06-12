### Mini-Sedric

This repo aims to show example of how mini-sedric home assignment can be solved.


### Requirements
- python 3.11.x
- [poetry 1.8.3](https://python-poetry.org/docs/)
- [FastAPI 0.111.0](https://fastapi.tiangolo.com/)
- docker 26.1.4 & docker compose 2.27.1

### Run local
To run app locally on `http://localhost:8000` type `poetry run fastapi dev main.py`.  
Though it's preferred to run it via `docker compose` so under root of repo type
`docker compose -f ./docker/docker-compose.dev.yml up`
