# Installation

1. Disable SELINUX. See distro docs.

2. Clone NOC to your favorite location. The default path is `/opt/noc`
```
git clone https://code.getnoc.com/noc/noc.git /opt/noc

cd /opt/noc/docker
```
3. Run noc-docker-setup.sh script to make dirs/permissions/config
```
./noc-docker-setup.sh -p all
```

4. Check the `./var/...-noc/etc/noc.conf` and edit configuration if required

5. Install `docker-compose`:  
see URL: https://docs.docker.com/compose/install/

6. Check if `docker` daemon is running.

7. Prepare to launch containers:
```
export DOCKER_CLIENT_TIMEOUT=200
docker compose up --no-start
```

8. Perform initial db initialization and migrations:
```
docker compose up migrate
```

Note: Be aware that command will run lots of noc daemons and expected
to be pretty slow.  
On laptops with SSD it takes about 2 minutes to get everything started

9. Start `NOC` in the docker: 
```
docker compose up -d 
```

10. Go to https://0.0.0.0 using default credentials:
```
Username: admin
Password: admin
```

## Limitations

* Only single node. No way to scale `noc` daemons to multihost.
* Databases are outside container in `./var/<composerprefix>-...` . 
* Only single pool: "default". No way to add equipment from different VRFs.
* Need 30G+ free space on block device
* SSD block device is highly recommended. It starts more than 2 minutes.

## Contributing

Contributions, issues and feature requests are welcome!

Feel free to check 
[issues page](https://code.getnoc.com/noc/noc/issues/).

Feel free to check Docker specific with tag `docker` 
[issues page](https://code.getnoc.com/noc/noc/-/merge_requests?label_name%5B%5D=docker).

Contact us:
----
* Official Site: https://getnoc.com/
* Community Guide: https://getnoc.com/community-guide/
