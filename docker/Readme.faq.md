FAQ:
----
Q: Where stored persistent data?

A: All persistent data stored in `./var/` dir.
```shell script
[root@localhost docker]# ls -1 ./var/
backup-data
backup-images
docker-clickhouse
docker-consul
docker-grafana
docker-mongo
docker-mongorestore
docker-nginx
docker-noc
docker-postgres
docker-postgresrestore
docker-promgrafana
docker-redis
docker-sentry
docker-vmagent
docker-vmalert
docker-vmmetrics
```

Q: To run `noc-dc`, I use a laptop without an ssd disk or an old server.
   When I start, I see intensive use of the drive that lasts more
   than 10 minutes. what should I do?

A: `noc-dc` consists of more than 30 containers,
    which leads to a very high load on the disk subsystem. 
    If you have a laptop or not very productive equipment, 
    do:
    
```shell script
docker-compose up -d mongodb-repl-set-init mongo postgres consul nginx_openssl \
traefik redis nginx clickhouse grafana migrate

docker-compose up -d
``` 

Q: What it looks like default output of `docker-compose ps`
 when all works as intended 

A:
```
% docker ps --format "{{.Names}}: {{.Status}}\t{{.Ports}}"
docker_nginx_1:                 Up 2 minutes	80/tcp, 0.0.0.0:443->443/tcp
docker_traefik_1:               Up 2 minutes	0.0.0.0:1200->1200/tcp, 80/tcp,
                                    0.0.0.0:8080->8080/tcp
docker_ping-default_1:          Up 2 minutes	1200/tcp
docker_trapcollector-default_1: Up 2 minutes	0.0.0.0:162->162/udp, 1200/tcp
docker_syslogcollector-default_1: Up 2 minutes	0.0.0.0:514->514/udp, 1200/tcp
docker_web_1:                   Up 2 minutes	1200/tcp
docker_card_1:                  Up 2 minutes	1200/tcp
docker_nbi_1:                   Up 2 minutes	1200/tcp
docker_chwriter_1:              Up 3 minutes	1200/tcp
docker_escalator_1:             Up 3 minutes	1200/tcp
docker_classifier-default_1:    Up 3 minutes	1200/tcp
docker_selfmon_1:               Up 3 minutes	1200/tcp
docker_correlator-default_1:    Up 3 minutes	1200/tcp
docker_bi_1:                    Up 3 minutes	1200/tcp
docker_mailsender_1:            Up 3 minutes	1200/tcp
docker_tgsender_1:              Up 3 minutes	1200/tcp
docker_sae_1:                   Up 3 minutes	1200/tcp
docker_datastream_1:            Up 3 minutes	1200/tcp
docker_datasource_1:            Up 3 minutes	1200/tcp
docker_login_1:                 Up 3 minutes	1200/tcp
docker_mib_1:                   Up 3 minutes	1200/tcp
docker_mrt_1:                   Up 3 minutes	1200/tcp
docker_scheduler_1:             Up 3 minutes	1200/tcp
docker_grafanads_1:             Up 3 minutes	1200/tcp
docker_discovery-default_1:     Up 3 minutes	1200/tcp                                                4170-4171/tcp
docker_clickhouse_1:            Up 4 minutes	8123/tcp, 9000/tcp, 9009/tcp
docker_grafana_1:               Up 4 minutes	3000/tcp
docker_activator-default_1:     Up 4 minutes	1200/tcp
docker_consul_1:                Up 4 minutes	8300-8302/tcp, 8301-8302/udp,
                                                8600/tcp, 8600/udp, 
                                                0.0.0.0:8500->8500/tcp
docker_mongo_1:                 Up 4 minutes	27017/tcp
docker_postgres_1:              Up 4 minutes (healthy)	5432/tcp
docker_redis_1:                 Up 4 minutes	6379/tcp                        
```

Q: Can i setup my ssl certificate?

A: Yes you can. you have to put it in `./var/<composeprefix>-nginx/ssl`
   and name it `noc.crt` and `noc.key`

Q: I need add my hosts for monitoring.

A: Read `./etc/noc/import/Readme.md` file

Q: What is '<composeprefix>'?
A: Its `docker-compose` project name. Default is directory name. 
   For more info see URL: 
   https://docs.docker.com/compose/reference/envvars/#compose_project_name 

Q: Can i use my own databases instead of new ? 

A: Glad you asked. Of course you can. Ensure that dockerized noc is not started
```
docker-compose down
``` 
Remove all files in:
```shell script
./var/<composeprefix>-postgres
./var/<composeprefix>-clickhouse/data
./var/<composeprefix>-mongo
```

Take a backup or shutdown your current noc and copy 
```
/var/lib/postgres -> ./var/<composeprefix>-postgres
/var/lib/clickhouse -> ./var/<composeprefix>-clickhouse/data
/var/lib/mongo -> ./var/<composeprefix>-mongo
```
fix permission
```shell script
./noc-docker-setup.sh -p perm
```

update passwords in `.env` and `./var/<composeprefix>-noc/etc/noc.conf` 
and start noc with: 
```
docker-compose up -d 
```
Thats it. Be aware that your copy will be doing same jobs.
And that can lead to a extreme server load. But here is a tric.
You can run 
```
docker-compose run migrate python commands/deactivate.py
```
It will unschedule all discovery jobs so you can run your copy without worries 

Q: Can i change files in that NOC install ?

A: Yes. See Readme.develop.md

Q: How to make \ restore a DB backup.

A: Use `docker-compose-storedb.yml` :
```shell script
docker-compose -f docker-compose-storedb.yml up
Creating docker_mongostore_1    ... done
Creating docker_postgresstore_1 ... done
....
docker_mongostore_1 exited with code 0
docker_postgresstore_1 exited with code 0
```
In `./var/<composeprefix>-mongorestore` and `./var/<composeprefix>-postgresrestore` stored
   DB backup files. 
```shell script
[root@localhost docker]# ls -1 ./var/<composeprefix>-mongorestore/
mongodb-20201013-19-20.archive
mongodb-20201024-18-51.archive
[root@localhost docker]# ls -1 ./var/<composeprefix>-postgresrestore
pg-20201013-19-20.dump
pg-20201024-18-51.dump
```
   For restore DB use `docker-compose-restore.yml`:
```shell script
docker-compose -f docker-compose-restoredb.yml up
Creating docker_postgresrestore_1 ... done
Creating docker_mongorestore_1    ... done
...
docker_postgresrestore_1 exited with code 0
docker_mongorestore_1 exited with code 0
```
  Important!!! Restored newest DB archive.

Q: I connect to the Internet through a proxy server.
   How do I configure the installation of all system components.

A: You need to set the environment variable 
   HTTPS_PROXY (necessarily in UPPER CASE) and the script 
   `./noc-docker-setup.sh` uses this variable to configure containers.
   You can check the current settings by running the command
   ```shell script
   env | grep -i proxy
    HTTPS_PROXY=http://<proxyIP>:<proxyPORT>
   ```
   If your proxy server address has changed - edit the file `.env.proxy`
   
Q: I want use RU language in `NOC` interface

A: Edit `./var/<composeprefix>-noc/etc/noc.conf`
   ```
   NOC_LANGUAGE=ru
   NOC_BI_LANGUAGE=ru
   NOC_CARD_LANGUAGE=ru
   NOC_LOGIN_LANGUAGE=ru
   NOC_WEB_LANGUAGE=ru
   NOC_LANGUAGE_CODE=ru
   ```
Q: I want to use default MongoDB cache. What i need do?

A: You need edit './var/<composeprefix>-noc/etc/noc.conf' and comment string:
   ```
   # NOC_CACHE_CACHE_CLASS=noc.core.cache.redis.RedisCache 
   ```

