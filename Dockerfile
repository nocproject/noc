#
# Base layer containing system packages and requirements
#
FROM python:3.9.10-slim-bullseye AS code
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PYTHONPATH=/opt \
    PROJ_DIR=/usr

COPY . /opt/noc/
WORKDIR /opt/noc/

ARG BUILD_PACKAGES="build-essential cmake gcc libffi-dev libmemcached-dev libssl-dev zlib1g-dev"

RUN \
    apt update && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    libffi7 \
    libjemalloc2 \
    libmemcached11 \
    libpq-dev \
    $BUILD_PACKAGES \
    && pip3 install --upgrade pip \
    && (./scripts/build/get-noc-requirements.py activator classifier cache-memcached cache-redis login-ldap login-pam login-radius prod-tools cython testing sender-kafka ping | pip3 install -r /dev/stdin )\
    && python3 ./scripts/deploy/install-packages requirements/web.json \
    && python3 ./scripts/deploy/install-packages requirements/card.json \
    && python3 ./scripts/deploy/install-packages requirements/bi.json \
    && cythonize -i /opt/noc/speedup/*.pyx \
    && mkdir /opt/nocspeedup \
    && cp /opt/noc/speedup/*.so /opt/nocspeedup \
    && find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python3 -m py_compile \
    && pip3 uninstall -y Cython \
    && apt remove --purge -y $BUILD_PACKAGES \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -d /opt/noc -M -r -u 1200 -U noc -s /bin/sh \
    && chown noc /opt/noc

VOLUME /opt/noc

EXPOSE 1200

# https://code.getnoc.com/noc/noc/-/issues/1480
#HEALTHCHECK --interval=10s --timeout=1s \
#    CMD curl -f http://0.0.0.0:1200/health/ || exit 1

#
# Developer's container
#
FROM code AS dev

RUN \
    apt update && apt-get install -y --no-install-recommends \
    snmp \
    vim \
    git \
    && (./scripts/build/get-noc-requirements.py dev | pip3 install -r /dev/stdin )\
    && rm -rf /var/lib/apt/lists/*

#
# Self-serving static ui files
#
FROM nginx:alpine AS static

RUN apk add --no-cache curl

COPY --from=code /usr/local/lib/python3.9/site-packages/django /usr/lib/python3.9/site-packages/django
COPY --from=code /opt/noc/ui /opt/noc/ui
