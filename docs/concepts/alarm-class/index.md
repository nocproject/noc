# Event Class

Describes the value of an event that enters the system, as well as the place where its settings are stored.

## Settings

* **Name** - the name of the event class. Must be unique, uses category notation separated by `|`
* **Text** - a block of event description settings
    * **Description** - a brief description
    * **Subject Template** - event title template displayed in the interface.
    * **Body template** - event body template displayed when viewing the event
    * **Symptoms** - description of possible symptoms that caused the event
    * **Probable Causes** - possible causes
    * **Recommended Actions** - actions to be taken to resolve the event
* **Severity**
    * **Default Severity** - 
    * **Unique** - Alarm can only exist in singular
    * **User Clearable** - The user can clear the alarm
    * **Ephemeral** - the alarm is not archived, it only exists in active form
    * **Reference** - list of key alarm variables
* **Variables**
    * **Name**
    * **Description**
    * **Default**
* **Data Sources**
    * **Name**
    * **Data source**
    * **Search**
* **Components**
    * **Name**
    * **Model** - data model
    * **Arguments**
        * *Parameter*
        * *Variable*
* **Root Cause**
    * **Name**
    * **Root** - reference to the alarm class
    * **Window** - correlation time window
    * **Condition** - current alarm matching conditions
    * **Match Condition** - matching criteria with the root cause (`Root`)
* **Topology RCA** - topology correlation, setting is not displayed, only performed for the `Ping Failed` class
* **Tasks** - ~~not used~~
* **Handlers**
    * **Open Handler**
    * **Clear Handler**
* **Plugins**
    * **Name**
    * **Configuration**
* Timer Settings (`Timing`)
    * (`Flap Condition`)
    * (`Flap Window`)
    * (`Flap Threshold`)
    * **Recovery Time**

## Description of Operation

The settings of the event class affect the operation of the [correlator](../../services-reference/correlator.md), 

## Naming Rules

Event class names use category separation with the `|` symbol: `<category1> | <category2> | <category3>`, 
for each manufacturer, a separate category is allocated, and manufacturer-specific classes are added to it.
