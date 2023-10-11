# hk check

<!-- prettier-ignore -->
!!! todo
    Describe *hk* check

This interface allows various operations to be performed based on the results of the past discovery. At the end of the discovery process, a [Handler](../../handlers-reference/index.md) with the [Allow Housekeeper](../../handlers-reference/housekeeper.md) interface is launched. The `Discovery check` is passed to it, and any methods from it are available.

## Requirements

You need to activate the following settings in the [Managed Object Profile Box tab](../../concepts/managed-object-profile/index.md#Box(Full_Polling)):

- `Housekeeping`: Enable `hk` check.
- **Handler**: Specify a [Handler](../../handlers-reference/index.md).
