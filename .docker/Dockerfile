FROM alpine:3.11 AS code

MAINTAINER Aleksey Shirokih <shirokih@nocproject.org>

WORKDIR /opt/noc
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    PYTHONPATH=/opt/noc:/opt:/usr/bin/python3.8 \
    VERSION=${VERSION} \
    NOC_LISTEN="auto:1200" \
    NOC_PYTHON_INTERPRETER=/usr/bin/python3

COPY . /opt/noc

RUN apk add --update --no-cache \
    ca-certificates \
    libpq \
    py3-cffi \
    py3-numpy \
    py3-pip \
    snappy \
    tzdata \
    libmemcached \
    curl \
    proj
RUN apk add --no-cache --virtual .build-deps \
    git \
    build-base \
    cyrus-sasl-dev \
    cython \
    cython-dev \
    gcc \
    libffi-dev \
    libmemcached-dev \
    libressl-dev \
    musl-dev \
    postgresql-dev \
    python3-dev \
    zlib-dev \
    cmake \
    proj-util \
    proj-dev \
    && pip3 install --src=/tmp/src --no-cache --trusted-host cdn.getnoc.com --find-links https://cdn.getnoc.com/npkg/ --upgrade -r /opt/noc/requirements/docker.txt \
    && python3 ./scripts/deploy/install-packages requirements/web.json \
    && python3 ./scripts/deploy/install-packages requirements/card.json \
    && python3 ./scripts/deploy/install-packages requirements/bi.json \
    && find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python3 -m py_compile \
    && /usr/bin/cythonize -i speedup/*.pyx \
    && apk del -r .build-deps \
    && adduser -h /opt/noc -s /bin/sh -S -D -H -u 1200 noc \
    && chown noc /opt/noc

EXPOSE 1200

VOLUME /opt/noc
VOLUME /usr/lib/python3.8/site-packages/django

FROM code AS dev

RUN apk add --update vim \
    python-dev \
    gcc musl-dev \
    && pip3 install pudb ipython \
    && apk del python-dev gcc musl-dev \
    && rm -rf /var/cache/apk/* /root/.cache/pip

HEALTHCHECK --interval=10s --timeout=1s \
    CMD curl -f http://0.0.0.0:1200/health/ || exit 1

FROM nginx:alpine AS static

RUN apk add --no-cache curl

COPY --from=code /usr/lib/python3.8/site-packages/django /usr/lib/python3.8/site-packages/django
COPY --from=code /opt/noc/ui /opt/noc/ui

