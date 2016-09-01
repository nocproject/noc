#!/bin/bash

mongo_ip="192.168.1.38"
pg_ip="192.168.1.38"
image="registry.gitlab.com/nocproject/docker-noc"
image_version="upstream"
update_delay="1s"
command_omap="python ./services/omap/service.py"
command_test="sleep 3600"

docker service create --name omap \
        --network noc-network \
        -e NOC_PG_HOST="${pg_ip}" \
        -e NOC_MONGO_HOST="${mongo_ip}" \
        -e NOC_PG_USER=noc \
        -e NOC_PG_PASSWORD=noc \
        --update-delay ${update_delay} \
        ${image}:${image_version} \
        ${command_omap}

docker service create --name test \
        --network noc-network \
        -e NOC_PG_HOST="${pg_ip}" \
        -e NOC_MONGO_HOST="${mongo_ip}" \
        -e NOC_PG_USER=noc \
        -e NOC_PG_PASSWORD=noc \
        --update-delay ${update_delay} \
        ${image}:${image_version} \
        ${command_test}