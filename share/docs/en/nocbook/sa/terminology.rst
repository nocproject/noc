Terminology
***********

* Managed Object - A piece of equipment or service, operated by Service Activation
* Profile - A representations of equipment class containing equipment capabilities and behavior specifics. (See SupportedEquipment for a list of profiles)
* Access scheme - Transport application protocol used to access equpment (Telnet, SSH, HTTP)
* SAE - Service Activation Engine. A hearth of **sa** module. Separated process responsible for dispatching tasks between activators and performing periodic tasks.
* Activator - Separate processes responsible for mediation with equipment.
* Network Domain - Logically, Physically or Administratively separated part of network. Examples: VRF, LAN behind NAT, city's part of network, etc. Direct communication between Network Domains is not necessary.