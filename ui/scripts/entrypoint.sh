#!/bin/sh
envsubst '$SERVER_NAME $BACKEND_URL' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
exec "$@"