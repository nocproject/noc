# Alarm Severity

Alarm impact on the network.

## Settings

![Alarm Severity Warning Form](alarm-severity-warning-form.png)

* **Name** - the name of the severity. Must be unique and displayed in the alarm.
* **Description** - a brief description.
* **Severity** - numerical severity level.
* **Min Weight** - minimum weight [Weight](../../fault-management/index.md#severity-and-weight) that an alarm must have to be assigned severity.
* **Sound** - sound played when an alarm of this weight appears.
* **Volume** - sound volume (0 - mute).

## Description of Operation

The basic level of an alarm defines the *minimum* and *maximum* values of the alarm's weight.
When an alarm is detected, the system must determine the number of monitoring objects, services, and users affected by the alarm.
The maximum severity level is the minimum value for the next level.
After detecting an alarm on specific equipment, the system calculates the alarm's weight and in which interval of basic severity values the alarm falls.
