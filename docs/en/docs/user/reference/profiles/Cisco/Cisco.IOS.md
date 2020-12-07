---
uuid: e44b7697-b75c-49b5-9df2-5e9021ce77a0
---
# Cisco.IOS Profile

`Cisco.IOS` profile supports wide range of
[Cisco Systems](index.md) network equipment running Cisco IOS software.

!!! info "Added in version"
    0.1

## Configuration

### Show firmware version

```
show version
```

### Show platform

```
show version
```

### Show configuration

Show current running configuration

```
show running-config
```

Show startup configuration

```
show startup-config
```

### Entering Configuration Mode

All configuration commands are entered in the configuration mode.
To enter configuration mode type

```
configure terminal
```

### Save Configuration

To save configuration changes type

```
copy running-config startup-config
```

### Create Local User

```
username <name> privelege 15 password <password>
```

### Enable SNMP

### Enable SSH

### Enable CDP

### Enable LLDP

## Supported Scripts

{{ supported_scripts("Cisco.IOS") }}

## Known Issues

* IOS 12.2SE got LLDP support starting from 12.2(33)SE, but
  due to several bugs it is recommended to use 12.2(50)SE or later
  if you planning to use LLDP discovery.

## Used Commands
`Cisco.IOS` profile emits following commands. Ensure they are
available for NOC user:

* show version
* show running-config
* show startup-config
