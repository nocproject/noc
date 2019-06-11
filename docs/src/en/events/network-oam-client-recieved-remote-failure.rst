.. _event-class-network-oam-client-recieved-remote-failure:

==============================================
Network | OAM | Client Recieved Remote Failure
==============================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Client has received a remote failure indication from its remote peer

Symptoms
--------
.. todo::
    Describe Network | OAM | Client Recieved Remote Failure symptoms

Probable Causes
---------------
The remote client indicates a Link Fault, or a Dying Gasp (an unrecoverable local failure), or a Critical Event in the OAMPDU. In the event of Link Fault, the Fnetwork administrator may consider shutting down the link.

Recommended Actions
-------------------
In the event of a link fault, consider shutting down the link.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
interface            Interface
reason               Failure reason
action               Response action
==================== ==================================================

Alarms
------
================= ======================================================================
Opening Event for :ref:`alarm-class-environment-total-power-loss`
================= ======================================================================
