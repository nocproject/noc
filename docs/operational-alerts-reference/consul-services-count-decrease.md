# ConsulServicesCountDecrease

1. Go to the node where the service that disconnected from Consul is running.
2. Check the service status: `./noc status <service name>`
3. Check the service logs at the path: `/var/log/noc`

Next, take the following actions until the service is restored in Consul:
1. Restart the module: `./noc restart <service name>`
2. Deregister and register the service in Consul: `consul services deregister <service name.json>`
3. Register the service in Consul: `consul services register <service name.json>`
4. Reload Consul: `consul reload`
5. Increase the limits in the configuration file: `/etc/consul/config.json`
``` json
"limits": {
    "http_max_conns_per_client": 1000
}
```
6. Reload Consul: `consul reload`
