ARG DOCKER_IMAGE_HOST
ARG PYTHON_VERSION=3.13

##
##  BUILD STAGE
##

FROM ${DOCKER_IMAGE_HOST}python:${PYTHON_VERSION}-alpine AS builder

#
#   system packages
#
RUN apk add --no-cache curl ca-certificates \
 && curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --yes \
 && mv /root/.local/bin/uv* /usr/local/bin/

#
#   dependencies
#
COPY pyproject.toml uv.lock /

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync ----compile-bytecode --group test && \
    (uv sync ----compile-bytecode --only-group shared || true) && \
    (uv sync ----compile-bytecode --only-group peer || true)


##
##  RUNTIME STAGE
##
FROM ${DOCKER_IMAGE_HOST}python:${PYTHON_VERSION}-alpine AS runtime

#
#   pre-built dependencies
#
COPY --from=builder /.venv /.venv
# NOTE: prepend to use the .venv python instead of system python
ENV PATH=/.venv/bin:$PATH

#
#   source code and tests
#
COPY artefacts /artefacts
COPY src /src
COPY tests /tests
COPY pytest.ini /pytest.ini
COPY .coveragerc /.coveragerc

RUN cat artefacts/extra_cert.crt >> "$(python -m certifi)" || true

CMD ["python", "-m", "src"]
