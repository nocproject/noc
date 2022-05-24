# Message Storm Protection

Message Storm Protection works as follows.

All actions are carried out in one of two places:
1. in a service that uses Storm Protection - by calling methods of the `StormProtection` instance
2. in the `StormProtection` instance itself in the `storm_round_handler` handler, which runs periodically with an interval of `storm_round_duration` seconds. The handler performs "talcative" flag changes and other actions basing on the results of analyzing the data accumulated over the time since the previous launch (verification round).

The following actions must be carried out in the service:
* creation and initialization of the `StormProtection` instance
* updating the message counter when a new message arrives (`update_messages_counter` method)
* implementation of reaction to arrival of a new message according to current parameters, that is, according to parameters calculated for ended period `storm_round_handler`. For "talkative" devices (`device_is_talkative` method), depending on `cfg.storm_policy`, the message is either blocked, or an alarm is raised, or both.

In the `storm_round_handler` handler, the following actions are performed for all monitored devices:
* setting or resetting the device's "talkative" flag
* reset the messages counter
* changing the record's time to live counter (field `ttl`) in the monitored devices table. If it has reached the limit value of `storm_record_ttl`, then the record is deleted (this is a device from which messages do not come and it should be deleted from the devices table to save memory)
* clear the alarm if it was raised, and the "talkative" flag has already been removed.