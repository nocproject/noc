# Message Storm Protection

## Purpose

Message storm protection is intended for use in collector services, that is, services that receive messages from devices over the UDP protocol or any other. At the moment, this condition is satisfied by the services `syslogcollector` and `trapcollector'.

Message Storm protection allows you to block messages or perform other actions in accordance with the policy when too many messages arrive from any of the devices without preventing the arrival of messages from other devices.

## Service Requirements

The service class must have an attribute containing *device configurations*, which includes at least the following fields:
* id - ID of the managed object
* partition - partition
* storm_policy - storm protection policy
* storm_threshold - storm protection message threshold

Its name is set in the module `stormprotection.py ` by the COLLECTOR_CONFIG_ATTRNAME constant.

## Working principle

Protection is provided by using the `noc.core.service.stormprotection.StormProtection`. When initializing an object of this class, a periodically repeating process is started - *round of verification*. During the verification round, data is accumulated on the number of incoming messages from each of the devices. At the end of the round, the fact that the number of received messages exceeds the threshold for enabling protection for this device is determined. If the threshold is exceeded, then actions are taken in accordance with the storm protection policy for this device. This information is stored and further used during the next round in relation to all messages coming to the service collector.

The above actions are performed automatically in the 'StormProtection' class. In the service itself, in addition to creating the `StormProtection` object and initializing it, it is necessary to execute the `process_messages` method when receiving each message. It will perform the following actions:
* increase the message counter for the device by one
* performs actions in accordance with the current status of exceeding the device's message threshold - raises an alarm if it has not been raised yet
* as a result, it will return a flag - whether the message needs to be blocked in the service or not

The message is blocked in the service itself by *not sending* the message, for example by exiting the appropriate method.

Example code for using message storm protection:

```python
# creating and initializing `StormProtection` instance
class TrapCollectorService(FastAPIService):
    async def on_activate(self):
        ...
        self.storm_protection = StormProtection(
            config.trapcollector.storm_round_duration,
            config.trapcollector.storm_threshold_reduction,
            config.trapcollector.storm_record_ttl,
            TRAPCOLLECTOR_STORM_ALARM_CLASS,
        )
        self.storm_protection.initialize()


# message processing and blocking if necessary
class TrapServer(UDPServer):
    def on_read(self, data: bytes, address: Tuple[str, int]):
        ...
        if cfg.storm_policy != "D":
            need_block = self.service.storm_protection.process_message(address[0])
            if need_block:
                return
```

## Description of methods of the `StormProtection` class

* `initialize()` - initialize the object
* `pocess_message(ip_address: str)` - message processing for the specified device. Performs the following actions:
  - increments the message counter for the device by one
  - performs actions in accordance with the current status of exceeding the device message threshold - raises an accident if it has not been raised yet
  - returns a sign as a result - whether the message needs to be blocked in the service or not

## Additional actions of the `StormProtection` object

In the object of the `StormProtection` class, the following additional actions are also performed automatically, if necessary:
* The alarm is closed if the protection from the device has been removed
* Records about devices from which messages have stopped coming are deleted from the device table (internal to the `StormProtection` class)

## Available settings

In the global settings (for a specific service):
* storm_round_duration - the duration of the verification round in seconds
* storm_threshold_reduction - the ratio of the shutdown threshold to the protection activation threshold
* storm_record_ttl - maximum lifetime (in rounds) of the device record in case of absence of messages

In the device settings (SourceConfig):
* storm_policy - storm protection policy
  - disable (Disabled - D)
  - block sender (Block - B)
  - raise alarm (Raise Alarm - R)
  - block sender and raise alarm (Block & Raise Alarm - A)
* storm_threshold - threshold number of messages per round to enable protection