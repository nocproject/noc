Install
-------
Disable SELINUX. See distro docs.

Clone NOC to your favorite location. In docs use default path `/opt/noc`
```
git clone https://code.getnoc.com/noc/noc.git /opt/noc

cd /opt/noc/docker
```
Run *pre.sh* script for make dirs\permissions\config
```
./noc-docker-setup.sh -p all
```
Check `./var/...-noc/etc/noc.conf` and edit config if needed

Install `docker-compose`- 
see URL: https://docs.docker.com/compose/install/

Check `docker` daemon is running.

Preparing to launch containers:
```
export DOCKER_CLIENT_TIMEOUT=200
docker-compose up --no-start
```
Run initial db init and migrations:
```
docker-compose up migrate
```
Wait for process to finish and then run noc itself.

Be aware that command will run lots of noc daemons and intended
to be pretty slow.  
On laptops with ssd it took at about 2 minutes to get everything started

Start `NOC` in docker: 
```
docker-compose up -d 
```
Go to https://0.0.0.0 with default credentials:
```
Username: admin
Password: admin
```

# Limitations

* Only single node. No way to scale `noc` daemons to multihost.
* Databases outside container in `./var/<composerprefix>-...` . 
* Only single pool "default". No way to add equipment from different vrfs.
* need 30G+ free space on block device
* SSD block device highly recommended. Start more that 2 minutes.

Contributing
----
Contributions, issues and feature requests are welcome!

Feel free to check 
[issues page](https://code.getnoc.com/noc/noc/issues/).

Feel free to check Docker specific with tag `docker` 
[issues page](https://code.getnoc.com/noc/noc/-/merge_requests?label_name%5B%5D=docker).

Contact us:
----
* Telegram group:  https://t.me/nocproject
* Official site: https://getnoc.com

