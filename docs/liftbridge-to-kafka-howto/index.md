# How to migrate from Liftbridge to Kafka


From some moment Liftbridge service didn't go well in production and become abandoned as a project, so we decided to switch main queue to Kafka


## Tower settings:

1. Uncheck all `liftbridge` and `nats` services, they won't be needed anymore.

2. Decide how many kafka node will be in your cluster. Possible amount: 1, 3, 5. 1 is a minimum cluster.

3. Check `kafka` services on needed nodes. Fill `Kafka Cluster Id` if you want, and make sure it's the same on each node. Fill JVM memory limit, 1Gb will be enough for small installation.

4. Please be sure that you use `consul` for your settings management(It happens when you have "consul://consul/noc," in `Config Load Preference Path` in main page `ENV` in `Tower`), otherwise you need to add settings to your local config file in `/opt/noc/etc/settings.yml`:

```
redpanda:
  addresses: kafka
msgstream:
  client_class: noc.core.msgstream.redpanda.RedPandaClient
```

5. Deploy

6. After success, you can delete old services from system

```
systemctl stop liftbridge
systemctl stop nats-server
systemctl disable liftbridge
systemctl disable nats-server
rm -rf /var/lib/liftbridge/*
```
