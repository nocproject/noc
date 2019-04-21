ARG IMAGE=${IMAGE}
FROM $IMAGE

MAINTAINER Aleksey Shirokih <shirokih@nocproject.org>

FROM nginx:alpine

RUN apk add --no-cache curl

COPY --from=0 /usr/lib/python2.7/site-packages/django /usr/lib/python2.7/site-packages/django
COPY --from=0 /opt/noc/ui /opt/noc/ui
