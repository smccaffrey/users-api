FROM python:3.10

WORKDIR /users_api

COPY pyproject.toml ./
COPY poetry.lock ./

RUN pip install poetry

# COPY . /backend

COPY ./ ./

RUN poetry install --no-root --no-interaction

CMD ["poetry", "run", "uvicorn", "users_api.app:app", "--host", "0.0.0.0", "--port", "3000"]
