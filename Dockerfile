FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR app/

COPY . .
RUN chmod +x /app/entrypoint.sh

RUN pip install poetry
RUN poetry install --no-interaction --no-ansi --without dev

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
