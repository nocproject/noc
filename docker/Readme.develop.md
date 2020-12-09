Custom
----
Use `./var/<COMPOSEPREFIX>-noc/custom` if need make custom:
* adapter for new hardware. See doc  
  https://kb.nocproject.org/pages/viewpage.action?pageId=22971074
* handler
* commands
* etc

Volume `./var/<COMPOSEPREFIX>-noc/custom` mapped to `/opt/noc_custom`
with RO perm.

FAQ
----
Q: I want fix script `/opt/noc/sa/profiles/MikroTik/RouterOS/get_version.py`.
 
A: Use `./var/<COMPOSEPREFIX>-noc/custom` directory.
   This directory is used for priority 
   file load for activator service. Create directory and `__init__.py` files
   ```shell script
   cd ./var/<COMPOSEPREFIX>-noc/custom
   mkdir -p ./sa/profiles/MikroTik/RouterOS/
   touch __init__.py
   touch ./sa/__init__.py
   touch ./sa/profiles/__init__.py
   touch ./sa/profiles/MikroTik/__init__.py
   touch ./sa/profiles/MikroTik/RouterOS/__init__.py
   ```
   Put you version `get_version.py` and restart `activator-default` container
   ```shell script
   docker-compose restart activator-default
   ```
Q: How to create one more `NOC` docker installation.

A: Use `-e <new_composeprefix>` in `noc-docker-setup.sh`
   (see `composeprefix` variables in `.env` file)
   ```shell script
./noc-docker-setup.sh -p all -e noc-ng
...
---
Created directory
----
mkdir: created directory ‘/opt/noc/docker/var/noc-ng-alertmanager’
....
mkdir: created directory ‘/opt/noc/docker/var/noc-ng-redis’
Write /opt/noc/docker/var/noc-ng-noc/etc/noc.conf
You can change the parameters NOC_PG_PASSWORD\NOC_MONGO_PASSWORD if you want
...
```
  **Important!!!** Check `NOC_PG_PASSWORD`,`PGPASSWORD` in `.env` and
  `./var/<new_composeprefix>-noc/etc/noc.conf`
  
Q: How to make \ restore a with different `composeprefix` DB backup.

A: Use `docker-compose-storedb.yml` :
```shell script
docker-compose -p <new_composeprefix> -f docker-compose-storedb.yml up
Creating <new_composeprefix>_mongostore_1    ... done
Creating <new_composeprefix>_postgresstore_1 ... done
....
docker_mongostore_1 exited with code 0
docker_postgresstore_1 exited with code 0
```
   In `./var/<new_composeprefix>-mongorestore` and 
   `./var/<new_composeprefix>-postgresrestore` stored
   DB backup files. 
```shell script
[root@localhost docker]# ls -1 ./var/<new_composeprefix>-mongorestore/
mongodb-20201013-19-20.archive
mongodb-20201024-18-51.archive
[root@localhost docker]# ls -1 ./var/<new_composeprefix>-postgresrestore
pg-20201013-19-20.dump
pg-20201024-18-51.dump
```
   For restore DB use `docker-compose-restore.yml`:
```shell script
docker-compose -f docker-compose-restoredb.yml up
Creating <new_composeprefix>_postgresrestore_1 ... done
Creating <new_composeprefix>_mongorestore_1    ... done
...
docker_postgresrestore_1 exited with code 0
docker_mongorestore_1 exited with code 0
```
  Important!!! Restored newest DB archive.

Q: I want add new HW support in NOC

A: 
   * add new vendor
   * add new object_profile
   * add new dir in sa/profiles
   * read https://kb.nocproject.org/pages/viewpage.action?pageId=22971074
   * use 'Q: I want fix script'

Thats it. Be aware of if you need to add new script it has to be added
to several services. Also you need discovery, sae and web.


OUTDATE!!!

Q: I need access to code that not worked in `custom` 

A: Run:
   ```shell script
   ./pre.sh -p all -c dev
   ```
   It download noc code in `./data/noc/code` 
   Edit `.env` file 
   ```shell script
   # NOC_CODE_PATH '/home' for PROD or '/opt/noc' for DEV
   NOC_CODE_PATH=/opt/noc
   ```
   and restart noc-dc
   ```shell script
   docker-compose down
   docker-compose up -d
   ```
   Code from `./data/noc/code` mount in `/opt/noc/` into all docker container.
   Edit and restart container.
