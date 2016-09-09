#!/bin/bash

image="registry.gitlab.com/nocproject/docker-noc"
image_version="upstream"
update_delay="1s"
# @todo dirname
data_path="/home/shirokih/projects/noc_data"
config_path="/home/shirokih/projects/noc/bundle/config"
scripts_path="/home/shirokih/projects/noc/bundle/scripts"
service_list="web login"
source_path="/home/shirokih/projects/noc"

docker service create \
        --name mongo \
        --network noc-network \
        --mount type=bind,source=$data_path/mongo,target=/data/db \
        --mount type=bind,source=$config_path/mongo,target=/data/configdb \
        --update-delay ${update_delay} \
        freeseacher/mongo:3.2.7 \
        --storageEngine wiredTiger --wiredTigerDirectoryForIndexes

docker service create \
        --name postgres \
        --network noc-network \
        --env NOC_PG_DB=noc \
        --env NOC_PG_USER=noc \
        --env NOC_PG_PASSWORD=noc \
        --mount type=bind,source=$data_path/postgres,target=/var/lib/postgresql/data \
        --mount type=bind,source=$scripts_path/postgres_init.sh,target=/docker-entrypoint-initdb.d/init-user-db.sh \
        --update-delay ${update_delay} \
        freeseacher/postgres:9.4


docker service create --name dev \
        --network noc-network \
        --env NOC_PG_HOST=postgres \
        --env NOC_MONGO_HOST=mongo \
        --env NOC_ENV=docker \
        --env NOC_DC=docker \
        --env NOC_NODE=docker \
        --env NOC_PG_DB=noc \
        --env NOC_PG_USER=noc \
        --env NOC_PG_PASSWORD=noc \
        --update-delay ${update_delay} \
        ${image}:dev \
        sleep 3600

for service in ${service_list};
do
        docker service create --name $service \
                --env NOC_PG_HOST=postgres \
                --env NOC_MONGO_HOST=mongo \
                --env NOC_ENV=docker \
                --env NOC_DC=docker \
                --env NOC_NODE=docker \
                --env NOC_PG_DB=noc \
                --env NOC_PG_USER=noc \
                --env NOC_PG_PASSWORD=noc \
                --network noc-network \
                --mount type=bind,source=$source_path,target=/opt/noc \
                --update-delay ${update_delay} \
                ${image}:${image_version} \
                python ./services/$service/service.py

done

docker service create \
        --name front \
        --network noc-network \
        --mount type=bind,source=$config_path/nginx,target=/etc/nginx \
        --mount type=bind,source=$source_path,target=/opt/noc \
        --publish 443:443 \
        --update-delay ${update_delay} \
        nginx:alpine
