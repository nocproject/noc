---
e1fea597-5f0e-45cf-bc3d-8770c58712c8
---

# hwlimits Model Interface

Interface be able to describe the hardware limits of the devices in the inventory models.
Limits can be set both on the chassis and for individual modules. Since the combination of module limits for modular equipment depends on too many factors, it is proposed not to implement it and to limit the control of limits for each individual module.

## Variables

| Name    | Type   | Description               | Required         | Constant         | Default |
| ------- | ------ | ------------------------- | ---------------- | ---------------- | --------|
|macs    | Int    | Limit for MAC addresses   | {{ no }} | {{ yes }} |         |
|queues    | Int    | Limit for QoS queues    | {{ no }} | {{ yes }} |         |
|ipv4_prefixes   | Int    | Limit for IPv4 prefixes on routing-table | {{ no }} | {{ yes }} |         |
|ipv6_prefixes   | Int    | Limit for IPv6 prefixes on routing-table | {{ no }} | {{ yes }} |         |

## Examples

```json
{
  "hwlimits": {
    "macs": 8192,
    "queues": 8,
    "ipv4_prefixes": 4294967295,
    "ipv6_prefixes": 4294967295
  }
}
```
