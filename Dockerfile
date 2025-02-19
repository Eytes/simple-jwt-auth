ARG ALPINE_VERSION=3.20
ARG PYTHON_VERSION=3.13
ARG PYTHON_TAG=${PYTHON_VERSION}-alpine${ALPINE_VERSION}
ARG UV_TAG=alpine${ALPINE_VERSION}


FROM ghcr.io/astral-sh/uv:${UV_TAG} AS uv_tool


FROM python:${PYTHON_TAG} AS dependencies
WORKDIR /app
COPY ./uv.lock ./pyproject.toml ./
COPY --from=uv_tool /usr/local/bin/uv /bin/
RUN uv export --format requirements-txt --no-hashes --no-dev -o ./requirements.txt


FROM python:${PYTHON_TAG}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app/src
COPY --from=dependencies /app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt
RUN addgroup -S appgroup && \
    adduser -SHD appuser -G appgroup && \
    chown appuser:appgroup -R /app
USER appuser
COPY --chown=appuser:appgroup ./src ./
EXPOSE 8080


ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "4", "--port", "8080"]