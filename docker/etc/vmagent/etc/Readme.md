Readme
----
https://prometheus.io - service for get metrics and alerting.
You need install *telegraf* and configure *docker* daemon for export metric 
from *docker* node. 

Install end configure *Telegraf* on localhost
------
Use search for doc

>  @google telegtaf install %%name of you linux distro%%

See https://github.com/influxdata/telegraf

Add */etc/telegtaf/telegraf.d/prometheus.conf file
```
# Configuration for the Prometheus client to spawn
[[outputs.prometheus_client]]
  ## Address to listen on
  listen = "0.0.0.0:9273"
  expiration_interval = "10s"
```
and restart *telegraf*
```
systemctl restart telegraf
```

Enable export Docker daemon metrics to Prometheus
------

Edit */etc/docker/daemon.json*
```
{
  "metrics-addr" : "127.0.0.1:9323",
  "experimental" : true
}
```
end reload Docker service

See https://docs.docker.com/config/thirdparty/prometheus/

FAQ
----
Q: Can i add alert rules files?
A: Put you custom rules in `./rules.custom.d/` and restart `prom` container 
