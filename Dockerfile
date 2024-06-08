# Basic Python image
FROM python:3.11-slim-bookworm AS python

# Build speedups
FROM python AS build
COPY .requirements/ /build/.requirements
COPY speedup/ /build/speedup/
WORKDIR /build
RUN \
    set -x\
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --upgrade pip \
    && pip install -r .requirements/cython.txt \
    && cythonize -i speedup/*.pyx

# Base layer containing system packages and requirements
FROM python AS code
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PYTHONPATH=/opt \
    PROJ_DIR=/usr \
    NOC_SPEEDUP_PATH=/opt/nocspeedup
COPY . /opt/noc/
COPY --from=build /build/speedup/*.so /opt/nocspeedup/
WORKDIR /opt/noc/

RUN \
    set -x \
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    libjemalloc2 \
    libpq-dev \
    && pip3 install --upgrade pip \
    && pip3 install\
    -r ./.requirements/node.txt\
    -r ./.requirements/bh.txt\
    -r ./.requirements/activator.txt\
    -r ./.requirements/classifier.txt\
    -r ./.requirements/cache-redis.txt\
    -r ./.requirements/login-ldap.txt\
    -r ./.requirements/login-pam.txt\
    -r ./.requirements/login-radius.txt\
    -r ./.requirements/prod-tools.txt\
    -r ./.requirements/testing.txt\
    -r ./.requirements/sender-kafka.txt\
    -r ./.requirements/ping.txt\
    && python3 ./scripts/deploy/install-packages requirements/web.json \
    && python3 ./scripts/deploy/install-packages requirements/card.json \
    && python3 ./scripts/deploy/install-packages requirements/bi.json \
    && python3 ./scripts/deploy/install-packages requirements/theme-noc.json \
    && (curl -L https://get.static-web-server.net/ | sed 's/sudo //g' | sh) \
    && find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python3 -m py_compile \
    && pip cache purge \
    && rm -rf /var/lib/apt/lists/* /tmp/*.whl\
    && useradd -d /opt/noc -M -r -u 1200 -U noc -s /bin/sh \
    && chown noc /opt/noc

# https://code.getnoc.com/noc/noc/-/issues/1480
#HEALTHCHECK --interval=10s --timeout=1s \
#    CMD curl -f http://0.0.0.0:1200/health/ || exit 1

#
# Developer's container
#
FROM code AS dev

RUN \
    apt-get update\
    && apt-get install -y --no-install-recommends \
    snmp \
    vim \
    git \
    nodejs \
    npm \
    && pip3 install\
    -r ./.requirements/dev.txt\
    -r ./.requirements/lint.txt\
    -r ./.requirements/test.txt\
    -r ./.requirements/docs.txt\
    && npm install -g eslint@8\
    && rm -rf /var/lib/apt/lists/*

#
# Self-serving static ui files
#
FROM nginx:alpine AS static

RUN apk add --no-cache curl

COPY --from=code /usr/local/lib/python3.11/site-packages/django /usr/lib/python3.11/site-packages/django
COPY --from=code /opt/noc/ui /opt/noc/ui
