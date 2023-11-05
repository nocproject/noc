# Firmware Policy

Firmware policy allows you to configure the system's behavior based on the device's firmware version. 
The following policies are available:

* Recommended - recommended firmware version for the device
* Acceptable - acceptable firmware version for the device
* Not Recommended - not recommended firmware version
* Denied - operation of this firmware version is prohibited

## Settings

The configuration starts in the {{ ui_path("Inventory", "Setup", "Firmware Policy") }} menu. 
After clicking the {{ ui_button("Add") }} button, a form for creating an external system with the following items opens:

* **Platform** - device platform restriction
* **Firmware Version** - firmware version
* **Condition** - condition for policy triggering (comparison with the selected version)
* **Policy** - policy
* **Description** - Text description of the policy
* **Labels** - assigned labels [Labels](../label/index.md)
* `Management`

Settings for the system's response to a denying policy (`Denied`) are also available. They are located in the `Box` tab 
in the object profile [Managed Object Profile](../managed-object-profile/index.md#Box(Full_Poll)), under `On Denied Firmware`:

* `Ignore` - ignore and continue polling
* `Ignore&Stop` - ignore and stop polling. Polling stops after `Version`.
* `Raise Alarm` - raise an alarm with the class `NOC | Managed Object | Denied Firmware` and continue polling.
* `Raise Alarm&Stop` - raise an alarm and stop polling

<!-- prettier-ignore -->
!!! info
    The `Stop` policy will only stop the current polling. The check will be repeated on the next poll.

## Operation Mechanism

Policy checking occurs during the version discovery [Version Discovery](../../discovery-reference/box/version.md). 
When determining the current policy, the deny priority is in effect. In other words, `Denied` policies are considered first, 
then `Not Recommended`, and so on. If a `Denied` policy is in effect, 
the system's behavior is determined by the `On Denied Firmware` settings of the [Managed Object Profile](../managed-object-profile/index.md#Box(Full_Poll)). 
This can be stopping polling at the version request stage, raising an alarm, or ignoring.

Also, in the policy, you can set allowed protocols for working with the device, but this functionality is not implemented.

If there are policies among the active ones on the [Managed Object](../managed-object/index.md) with labels [Labels](../label/index.md) 
that are allowed for assignment to the device, they will flow into its `effective_labels`.

## Display

The current policy is displayed in the device card (`Managed Object Card`). 
Also, in the report {{ ui_path("Service Activation", "Reports", "Managed Object Summary") }}.
When selecting the report type *By Version*, a column for the current policy will be displayed.
