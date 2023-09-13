---
uuid: bc075da2-7292-4335-976c-61594c45bc85
---
# Network | OAM | Client Recieved Remote Failure

Client has received a remote failure indication from its remote peer

## Symptoms

## Probable Causes

The remote client indicates a Link Fault, or a Dying Gasp (an unrecoverable local failure), or a Critical Event in the OAMPDU. In the event of Link Fault, the Fnetwork administrator may consider shutting down the link.

## Recommended Actions

In the event of a link fault, consider shutting down the link.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
reason | str | {{ no }} | Failure reason
action | str | {{ no }} | Response action

## Alarms

### Raising alarms

`Network | OAM | Client Recieved Remote Failure` events may raise following alarms:

Alarm Class | Description
--- | ---
[Environment \| Total Power Loss](../../../alarm-classes/environment/total-power-loss.md) | Total power loss
