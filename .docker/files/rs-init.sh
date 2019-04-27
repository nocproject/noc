#!/bin/bash

_wait_for_mongo_host() {
	local host=$1
	mongo --host $host --eval db
	while [ "$?" -ne 0 ]; do
		echo "== Waiting for host $host..."
		sleep 1
		mongo --host $host --eval db
	done
}

echo "== Waiting for all mongo hosts to be ready..."
mongo_config_host=""
for host in $MONGO_REPL_SET_HOSTS; do
	_wait_for_mongo_host $host
	mongo_config_host="$host"
done

mongo --host "$mongo_config_host" \
	--username "$MONGO_INITDB_ROOT_USERNAME" \
	--password "$MONGO_INITDB_ROOT_PASSWORD" \
	--authenticationDatabase admin <<-EOJS
		var rsConfig = {
			_id: "$MONGO_REPL_SET_NAME",
			members: []
		};
		"$MONGO_REPL_SET_HOSTS".split(' ').forEach(function (host, i) {
			rsConfig.members.push({
				_id: i,
				host: host + ":27017"
			});
		});
		rs.initiate(rsConfig);
	EOJS
