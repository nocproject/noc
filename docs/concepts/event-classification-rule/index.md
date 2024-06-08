# Event Class

Describes the value of an incoming event in the system and also the place to store its settings.

## Settings

* **Name** (`Name`) - the name of the event class. It must be unique and uses category notation separated by `|`
* **Text** (`Text`) - a block of settings for the text description of the event
    * **Description** (`Description`) - a brief description
    * **Subject Template** (`Subject Template`) - the event title template displayed in the interface.
    * **Body Template** (`Body template`) - the event body template displayed when viewing the event
    * **Symptoms** (`Symptoms`) - description of possible symptoms that triggered the event
    * **Probable Causes** (`Probable Cause`) - possible causes
    * **Recommended Actions** (`Recommended Actions`) - actions to take to resolve the event
* **Action** - system actions with the event
    * **Action** (`Action`)
        * **Drop** - stop processing the event
        * **Log** - Continue processing and save in events
        * **Archive** - Continue processing and move to archived events
    * **Link Event** (`Link Event`)
* **Variables** (`Vars`) - variables used in the event
    * **Name** (`Name`) - variable name
    * **Type** (`Type`) - variable type
    * **Required** (`Required`) - the variable must be filled in
    * **Match Suppress** (`Match Suppress`) - the variable is used in suppression detection
    * **Description** (`Description`) - a brief explanation
* **Disposition** (`Disposition`) - event processing rules, processed sequentially until the end or a stop (`Stop`) pointer is set
    * **Name** (`Name`) - name, must be unique
    * **Condition** (`Condition`) - condition for applying disposition
    * **Action** (`Action`) - actions when applied
        * `drop` - delete the event and stop processing
        * `ignore` - ignore the line
        * `raise` - send the event for processing to the correlator to create an alarm
        * `clear` - send the event for processing to the correlator to close the alarm
    * **Alarm Class** (`Alarm Class`) - Alarm class (applies to `raise` and `clear` actions)
    * **Stop** (`Stop`) - Stop processing when set
    * **Managed Object** (`Managed Object`) - Python expression for denoting the device (`ManagedObject`)
    * **Vars Mapping** (`Vars Mapping`)
* **Suppression** (`Suppression`) - event suppression settings
    * **Deduplication Window** (`Deduplication Window`)
    * **Suppression Window** (`Suppression Window`)
    * **Time To Live** (`TTL`)
* **Handlers** (`Handlers`) - a list of handlers [Handler](../handler/index.md) for execution
* **Plugins** (`Plugins`) - a list of plugins *not used*

## Description of Operation

Event class settings affect the operation of the [classifier](../../services-reference/classifier.md), 
and are assigned based on classification rules [Classification Rule](../event-classification-rule/index.md). If no suitable 
rule is found, default rules are triggered, or the class `Unknown | Default` is assigned:

* `Unknown | Syslog` - assigned to events based on `Syslog` for which no suitable rule is found
* `Unknown | SNMP Trap` - assigned to events based on `SNMP Trap` for which no suitable rule is found
* `Unknown | Default` - assigned to events if no match with any of the rules is achieved.

The event's time to live (`TTL`) allows you to avoid cluttering the database with unnecessary data. 
However, if the event has been forwarded for further processing, such as becoming an alarm, the TTL action is canceled.

## Naming Conventions

In the naming of event classes, categories are used with the `|` symbol: `<category1> | <category2> | <category3>`, 
and a separate category is allocated for each manufacturer, where specific classes for that manufacturer are recorded.
