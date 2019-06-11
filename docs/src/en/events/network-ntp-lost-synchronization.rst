.. _event-class-network-ntp-lost-synchronization:

====================================
Network | NTP | Lost synchronization
====================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

NTP synchronization with its peer has been lost

Symptoms
--------
.. todo::
    Describe Network | NTP | Lost synchronization symptoms

Probable Causes
---------------
NTP synchronization with its peer has been lost

Recommended Actions
-------------------
Perform the following actions:
   Check the network connection to the peer.
   Check to ensure that NTP is running on the peer.
   Check that the peer is synchronized to a stable time source.
   Check to see if the NTP packets from the peer have passed the validity tests specified in RFC1305.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
server_name          NTP server name
server_address       NTP server IP address
==================== ==================================================
