FROM alpine:3.8

MAINTAINER Aleksey Shirokih <shirokih@nocproject.org>

WORKDIR /opt/noc
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    PYTHONPATH=/opt/noc:/opt:/usr/bin/python2.7 \
    VERSION=${VERSION} \
    NOC_LISTEN="auto:1200"

COPY . /opt/noc

RUN apk add --update --no-cache \
    ca-certificates \
    libpq libssh2 \
    py-cffi \
    py-numpy \
    py-pip \
    snappy \
    tzdata \
    libmemcached \
    curl \
   && apk add --no-cache --virtual .build-deps \
        cyrus-sasl-dev \
        cython \
        cython-dev \
        gcc \
        libffi-dev \
        libmemcached-dev \
        libressl-dev \
        libssh2-dev \
        musl-dev \
        postgresql-dev \
        python-dev \
        zlib-dev \
    && pip install --no-cache --trusted-host cdn.getnoc.com --find-links https://cdn.getnoc.com/npkg/ --upgrade -r /opt/noc/requirements/docker.txt \
    && python ./scripts/deploy/install-packages requirements/web.json \
    && python ./scripts/deploy/install-packages requirements/card.json \
    && python ./scripts/deploy/install-packages requirements/bi.json \
    && find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python -m py_compile \
    && /usr/bin/cythonize -i speedup/*.pyx \
    && apk del -r .build-deps \
    && adduser -h /opt/noc -s /bin/sh -S -D -H -u 1200 noc \
    && chown noc /opt/noc

EXPOSE 1200

VOLUME /opt/noc
VOLUME /usr/lib/python2.7/site-packages/django
