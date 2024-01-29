FROM python:3.12.1-slim-bookworm as python

FROM python as python-build-stage

COPY ./requirements ./requirements
ARG REQUIREMENTS=./requirements/base.txt
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${REQUIREMENTS}

FROM python as python-run-stage

ARG APP_HOME=/netverse

WORKDIR ${APP_HOME}

# copy wheel dependencies from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ $(ls /wheels/*) \
	&& rm -rf /wheels/

COPY . ${APP_HOME}
