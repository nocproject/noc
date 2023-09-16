# ManagedObject Create MX Message

`object_deleted` message is generated wheh deleted [Managed Object](../concepts/managed-object/index.md).

## Message Headers

Message-Type
: Type of message. Always `object_deleted`.

Sharding-Key
: Key for consistent sharding.

Labels
: Managed Object's effective labels.

## Message Format

Message contains JSON object, containing objects of following structure


| Name                            | Type                 | Description                   |
| ------------------------------- | -------------------- | ----------------------------- |
| managed_object                  | Object {{ complex }} | Managed Object details        |
| {{ tab }} id                    | String               | Managed Object's ID           |
| {{ tab }} name                  | String               | Managed Object's Name         |
| {{ tab }} description           | String               | Managed Object's Description  |
| {{ tab }} address               | String               | Managed Object's Address      |
| {{ tab }} administrative_domain | Object {{ complex }} | Administrative Domain details |
| {{ tab2 }} id                   | String               | Administrative Domain's ID    |
| {{ tab2 }} name                 | String               | Administrative Domain's name  |
| {{ tab }} profile               | Object {{ complex }} | SA Profile details            |
| {{ tab2 }} id                   | String               | SA Profile's ID               |
| {{ tab2 }} name                 | String               | SA Profile's name             |
| {{ tab }} object_profile        | Object {{ complex }} | Object Profile details        |
| {{ tab2 }} id                   | String               | Object Profile's ID           |
| {{ tab2 }} name                 | String               | Object Profile's name         |
