FROM public.ecr.aws/amazonlinux/amazonlinux:2023 as build

## Non-root user and group
RUN dnf install -y shadow-utils
RUN groupadd -g 888 python && useradd -r -u 888 -g python python
ENV TASK_ROOT=/var/task
RUN mkdir "${TASK_ROOT}" && chown python:python "${TASK_ROOT}"
WORKDIR "${TASK_ROOT}"

# Python and wsgi server
RUN dnf install -y python3.11
RUN dnf clean all
USER 888
RUN python3.11 -m venv "${TASK_ROOT}"
ENV PATH="${TASK_ROOT}/bin:${PATH}"
RUN python3.11 -m ensurepip
RUN python3.11 -m pip install --no-cache-dir --disable-pip-version-check -U gunicorn uvicorn[standard]

# Project dependencies
COPY --chown=python:python requirements.prod.txt ./
RUN python3.11 -m pip install --no-cache-dir --disable-pip-version-check -U -r requirements.prod.txt

# Copy project source
COPY --chown=python:python src/api/*.py ./api/
COPY --chown=python:python src/api/lib/*.py ./api/lib/

# Copy non-secret environment variables.
# Note: docker just silently fails to create hidden files on the container (using COPY, RUN cp, RUN mv, etc...).
COPY --chown=python:python .env.dockerfile ./env

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "api.app:app"]
# Note: uvicorn workers are async, so we disable --timeout
# ref: https://docs.gunicorn.org/en/stable/settings.html#timeout
CMD ["--bind", ":5000", "--workers=4", "--timeout", "0"]
HEALTHCHECK --start-period=5s CMD curl -f http://localhost:5000/v1/healthz
