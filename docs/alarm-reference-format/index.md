# Alarm Refefence Format

Alarm reference is a kind of distinguisher used for direct alarm addressing and for deduplication.
Open alarms with same references are virtually the same and will be handled as one alarm.

References are assigned into the namespaces, each with unique prefix:

* `e` - [Event Reference](#event-reference)
* `g` - [Group Reference](#group-reference), including
  * `g:m` - [Maintenance Reference](#maintenance-reference)
  * `g:u` - [User Reference](#user-reference)
* `p` - [Ping Reference](#ping-reference)

## Event Reference

Generated internally by [correlator](../services-reference/correlator.md) service during the processing of events.

Simple format (without variables):

```
e:<managed object id>:<alarm class id>
```

Complex format (with variables)

```
e:<managed object id>:<alarm class id>:<var1>:...:<varN>
```

Where:

* `e` - Event reference namespace
* `<managed object id>` - ID of related managed object
* `<alarm class id>` - ID of related alarm class
* `<var1>`, .., `<varN>` - Appropriate alarm class `reference` variable values.
  `\` will be replaced with `\\`, `:` will be replaced with `\:`

Alarm classes without additional `reference` variables will raise only one alarm per class.

## Group Reference

Common namespace for various group alarms. Following group subnamespaces are reserved for system use:

* `g:m` - [Maintenance Reference](#maintenance-reference)
* `g:u` - [User Reference](#user-reference)

### Maintenance Reference

Created automatically for all active maintenances.

Format:

```
g:m:<maintenance id>
```

Where:

* `<maintenance id>` - ID of the maintenance record.

### User Reference

Created by user to group and hold alarms in work.

Format:

```
g:u:<user id>
```

* `<user id>` - ID of the holding user.
  
## Ping Reference

Used by `ping` service to address `Ping Failed` alarms.

Format:

* `p:<managed object id>`
  
Where:

* `<managed object id>` - ID of the managed object.
