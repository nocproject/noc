# Basic Python image
FROM python:3.12-slim-trixie AS python

# Base layer containing system packages and requirements
FROM python AS code
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PYTHONPATH=/opt \
    PROJ_DIR=/usr
COPY . /opt/noc/
WORKDIR /opt/noc/
RUN \
    set -x \
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    libjemalloc2 \
    libpq-dev \
    iproute2 \
    && pip3 install --upgrade pip \
    && pip install -e .[bh,activator,classifier,cache-redis,node,login-ldap,login-pam,login-radius,prod-tools,testing,sender-kafka,ping] \
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
ENV PNPM_HOME="/root/.local/share/pnpm" \
    PATH="/root/.local/share/pnpm:$PATH"

RUN \
    apt-get update\
    && apt-get install -y --no-install-recommends \
    snmp \
    vim \
    git \
    && (curl -fsSL https://get.pnpm.io/install.sh | bash -) \
    && pip install --upgrade pip\
    && pip install -e .[dev,docs,lint,test]\
    && rm -rf /var/lib/apt/lists/*
RUN pnpm env use --global 22\
    && (cd ui && pnpm i)

# Devcontainer
# Node.js layer
FROM python AS nodejs
RUN \
    set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && (curl -fsSL https://get.pnpm.io/install.sh | bash -) \
    && rm -rf /var/lib/apt/lists/*

ENV PNPM_HOME="/root/.local/share/pnpm" \
    PATH="/root/.local/share/pnpm:$PATH"

RUN pnpm env use --global 22

FROM nodejs AS devcontainer
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/local/bin/python3 \
    NOC_LISTEN="auto:1200" \
    PROJ_DIR=/usr\
    NODE_OPTIONS=--max-old-space-size=8192\
    PNPM_HOME=/root/.local/share/pnpm\
    PATH=$PNPM_HOME:$PATH
COPY docker-entrypoint.sh /usr/local/bin/
COPY . /workspaces/noc/
WORKDIR /workspaces/noc/
RUN \
    set -x \
    && apt-get update\
    && apt-get install -y --no-install-recommends \
    bzip2 \
    curl \
    libjemalloc2 \
    libpq-dev \
    snmp \
    vim \
    git \
    && pip3 install --upgrade pip \
    && pip install -e .[bh,activator,classifier,cache-redis,dev,docs,lint,node,test,login-ldap,login-pam,login-radius,prod-tools,testing,sender-kafka,ping] \
    && pip cache purge \
    && rm -rf /var/lib/apt/lists/* /tmp/*.whl \
    && chmod +x /usr/local/bin/docker-entrypoint.sh
    
VOLUME ["/workspaces/noc/ui/node_modules"]
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/bin/bash"]

#
# Self-serving static ui files
#
FROM nginx:alpine AS static

RUN apk add --no-cache curl

COPY --from=code /usr/local/lib/python3.12/site-packages/django /usr/lib/python3.1/site-packages/django
COPY --from=code /opt/noc/ui /opt/noc/ui
