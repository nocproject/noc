# Basic Python image
FROM python:3.12-slim-trixie AS python
ENV \
    PYTHONPATH=/opt
RUN \
    set -x \
    && apt-get update\
    && apt-get dist-upgrade -y\
    && apt-get clean\
    && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    ca-certificates \
    libjemalloc2 \
    libpq-dev \
    iproute2 \
    && (curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh)

# Base layer containing system packages and requirements
FROM python AS code
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PROJ_DIR=/usr
COPY . /opt/noc/
WORKDIR /opt/noc/
RUN \
    set -x \
    && uv pip install --system -e .[bh,activator,classifier,cache-redis,node,login-ldap,login-pam,login-radius,prod-tools,testing,sender-kafka,ping] \
    && python3 ./scripts/deploy/install-packages requirements/web.json \
    && python3 ./scripts/deploy/install-packages requirements/card.json \
    && python3 ./scripts/deploy/install-packages requirements/bi.json \
    && python3 ./scripts/deploy/install-packages requirements/theme-noc.json \
    && (curl -L https://get.static-web-server.net/ | sed 's/sudo //g' | sh) \
    && find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python3 -m py_compile \
    && uv cache clean \
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
ENV\
    PATH=$PATH:/opt/node_modules/.bin
RUN \
    apt-get update\
    && apt-get install -y --no-install-recommends \
    snmp \
    vim \
    git \
    && uv pip install --system -e .[dev,docs,lint,test]\
    && uv cache clean \
    && (curl -fsSL https://deb.nodesource.com/setup_22.x | bash -)\
    && apt-get install -y --no-install-recommends nodejs \
    && (cd ui/ && npm install) \
    && mv ui/node_modules /opt\
    && rm -rf /var/lib/apt/lists/*

FROM python AS devcontainer
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PROJ_DIR=/usr\
    NODE_OPTIONS=--max-old-space-size=8192\
    PATH=$PATH:/workspaces/node_modules/.bin
COPY . /workspaces/noc/
WORKDIR /workspaces/noc/
RUN \
    set -x \
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    snmp \
    git \
    && uv pip install --system -e .[bh,activator,classifier,cache-redis,dev,docs,lint,node,test,login-ldap,login-pam,login-radius,prod-tools,testing,sender-kafka,ping] \
    && uv cache clean \
    && (curl -fsSL https://deb.nodesource.com/setup_22.x | bash -)\
    && apt-get install -y --no-install-recommends nodejs \
    && (cd ui/ && npm install) \
    && mv ui/node_modules /workspaces\
    && rm -rf /var/lib/apt/lists/* /tmp/*.whl

#
# Self-serving static ui files
#
FROM nginx:alpine AS static

RUN apk add --no-cache curl

COPY --from=code /usr/local/lib/python3.12/site-packages/django /usr/lib/python3.1/site-packages/django
COPY --from=code /opt/noc/ui /opt/noc/ui
