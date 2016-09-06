#!/bin/sh

docker-compose stop # just stop
docker-compose rm -vf # remove containers
echo "Removing dbs"
sudo rm -r ../../noc_data/mongo ../../noc_data/postgres   #drop dbs
echo "Removing so files"
sudo rm ../speedup/*.so # drop cython