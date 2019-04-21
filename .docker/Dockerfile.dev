ARG IMAGE=${IMAGE}
FROM $IMAGE

MAINTAINER Aleksey Shirokih <shirokih@nocproject.org>

RUN apk add --update vim \
    python-dev \
    gcc musl-dev \
    && pip install pudb ipython \
    && apk del python-dev gcc musl-dev \
    && rm -rf /var/cache/apk/* /root/.cache/pip


HEALTHCHECK NONE 
