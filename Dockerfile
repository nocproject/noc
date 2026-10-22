# Basic Python image
FROM python:3.13-slim-trixie AS python
ENV \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPYCACHEPREFIX=/tmp/noc-pycache
RUN \
    set -x \
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    ca-certificates \
    iproute2 \
    && (curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh)

# Build web
FROM --platform=$BUILDPLATFORM node:24-trixie-slim AS build-ui
COPY . /opt/noc
WORKDIR /opt/noc
ENV \
    DEBIAN_FRONTEND=noninteractive
RUN\
    set -x\
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    ca-certificates \
    && corepack enable \
    && corepack prepare pnpm@10.33.0 --activate \
    && (cd ui/ && pnpm install --frozen-lockfile) \    
    && ./scripts/build/build-ui

# Base layer containing system packages and requirements
FROM python AS code
ENV \
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PROJ_DIR=/usr \
    PYTHONPATH=/opt/noc/src
COPY . /opt/noc/
COPY --from=build-ui /opt/noc/ui/dist/ /opt/noc/src/noc/ui/
WORKDIR /opt/noc/
RUN \
    set -x \
    && uv pip install --system -e . \
    && find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python3 -m py_compile \
    && uv cache clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*.whl\
    && useradd -d /opt/noc -M -r -u 1200 -U noc -s /bin/sh \
    && chown noc /opt/noc

FROM python AS devcontainer
ENV \
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PYTHONPATH=/workspaces/noc/src \
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
    && uv pip install --system build -e .[dev,docs,lint,test,testing] \
    && uv cache clean \
    && (curl -fsSL https://deb.nodesource.com/setup_24.x | bash -)\
    && apt-get install -y --no-install-recommends nodejs \
    && corepack enable \
    && corepack prepare pnpm@10.33.0 --activate \
    && (cd ui/ && pnpm install --frozen-lockfile) \
    && mv ui/node_modules /workspaces\
    && rm -rf /var/lib/apt/lists/* /tmp/*.whl
