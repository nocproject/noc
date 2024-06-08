# Config Fetching

`Fetching` is the process of retrieving of device configuration.
Performed by [config check](../discovery-reference/box/config.md) of [box discovery](../discovery-reference/box/index.md).
According to the `Config Policy` setting in [Managed Object Profile](../concepts/managed-object-profile/index.md)
there are two method possible:

- Script
- Download from external storage

## Fetching via script

[get_config](../scripts-reference/get_config.md) script for target platform is necessary.
Usually it is the second script besides [get_version](../scripts-reference/get_version.md) to implement.

## Fetching from external storage

`Discovery` can download configuration from [External Storage](../concepts/external-storage/index.md).
Supposed that configuration supplied to storage via external process:
device uploads config by itself or some third-party system (like RANCID),
performs all dirty work for us. Fetching from external storage is
the integrated feature of `Discovery` and provided out-of-the box.
