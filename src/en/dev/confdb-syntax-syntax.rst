.. _dev-confdb-syntax-syntax:

=============
ConfDB Syntax
=============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

*Normalized Config* is the device-independent configuration representation.
Raw device config processed by *Config Tokenizer* and converted to
the list of *Tokens*. *Tokens* processed by *Config Normalizer*
and became *Normalized Config*.

Syntax
------

* :ref:`meta<dev-confdb-syntax-meta>`

  * :ref:`id<dev-confdb-syntax-meta-id>`

    * :ref:`\<id\><dev-confdb-syntax-meta-id-id>`

  * :ref:`profile<dev-confdb-syntax-meta-profile>`

    * :ref:`\<profile\><dev-confdb-syntax-meta-profile-profile>`

  * :ref:`vendor<dev-confdb-syntax-meta-vendor>`

    * :ref:`\<vendor\><dev-confdb-syntax-meta-vendor-vendor>`

  * :ref:`platform<dev-confdb-syntax-meta-platform>`

    * :ref:`\<platform\><dev-confdb-syntax-meta-platform-platform>`

  * :ref:`version<dev-confdb-syntax-meta-version>`

    * :ref:`\<version\><dev-confdb-syntax-meta-version-version>`

  * :ref:`object-profile<dev-confdb-syntax-meta-object-profile>`

    * :ref:`id<dev-confdb-syntax-meta-object-profile-id>`

      * :ref:`\<id\><dev-confdb-syntax-meta-object-profile-id-id>`

    * :ref:`name<dev-confdb-syntax-meta-object-profile-name>`

      * :ref:`\<name\><dev-confdb-syntax-meta-object-profile-name-name>`

    * :ref:`level<dev-confdb-syntax-meta-object-profile-level>`

      * :ref:`\<level\><dev-confdb-syntax-meta-object-profile-level-level>`

  * :ref:`segment<dev-confdb-syntax-meta-segment>`

    * :ref:`id<dev-confdb-syntax-meta-segment-id>`

      * :ref:`\<id\><dev-confdb-syntax-meta-segment-id-id>`

    * :ref:`name<dev-confdb-syntax-meta-segment-name>`

      * :ref:`\<name\><dev-confdb-syntax-meta-segment-name-name>`

  * :ref:`management<dev-confdb-syntax-meta-management>`

    * :ref:`address<dev-confdb-syntax-meta-management-address>`

      * :ref:`\<address\><dev-confdb-syntax-meta-management-address-address>`

    * :ref:`protocol<dev-confdb-syntax-meta-management-protocol>`

      * :ref:`\<protocol\><dev-confdb-syntax-meta-management-protocol-protocol>`

  * :ref:`tags<dev-confdb-syntax-meta-tags>`

    * :ref:`\*\<tag\><dev-confdb-syntax-meta-tags-tag>`

* :ref:`system<dev-confdb-syntax-system>`

  * :ref:`hostname<dev-confdb-syntax-system-hostname>`

    * :ref:`\<hostname\><dev-confdb-syntax-system-hostname-hostname>`

  * :ref:`domain-name<dev-confdb-syntax-system-domain-name>`

    * :ref:`\<domain_name\><dev-confdb-syntax-system-domain-name-domain_name>`

  * :ref:`prompt<dev-confdb-syntax-system-prompt>`

    * :ref:`\<prompt\><dev-confdb-syntax-system-prompt-prompt>`

  * :ref:`clock<dev-confdb-syntax-system-clock>`

    * :ref:`timezone<dev-confdb-syntax-system-clock-timezone>`

      * :ref:`\<tz_name\><dev-confdb-syntax-system-clock-timezone-tz_name>`

        * :ref:`offset<dev-confdb-syntax-system-clock-timezone-tz_name-offset>`

          * :ref:`\<tz_offset\><dev-confdb-syntax-system-clock-timezone-tz_name-offset-tz_offset>`

    * :ref:`source<dev-confdb-syntax-system-clock-source>`

      * :ref:`\<source\><dev-confdb-syntax-system-clock-source-source>`

  * :ref:`user<dev-confdb-syntax-system-user>`

    * :ref:`\*\<username\><dev-confdb-syntax-system-user-username>`

      * :ref:`uid<dev-confdb-syntax-system-user-username-uid>`

        * :ref:`\<uid\><dev-confdb-syntax-system-user-username-uid-uid>`

      * :ref:`full-name<dev-confdb-syntax-system-user-username-full-name>`

        * :ref:`\<full_name\><dev-confdb-syntax-system-user-username-full-name-full_name>`

      * :ref:`class<dev-confdb-syntax-system-user-username-class>`

        * :ref:`\*\<class_name\><dev-confdb-syntax-system-user-username-class-class_name>`

      * :ref:`authentication<dev-confdb-syntax-system-user-username-authentication>`

        * :ref:`encrypted-password<dev-confdb-syntax-system-user-username-authentication-encrypted-password>`

          * :ref:`\<password\><dev-confdb-syntax-system-user-username-authentication-encrypted-password-password>`

        * :ref:`ssh-rsa<dev-confdb-syntax-system-user-username-authentication-ssh-rsa>`

          * :ref:`\*\<rsa\><dev-confdb-syntax-system-user-username-authentication-ssh-rsa-rsa>`

        * :ref:`ssh-dsa<dev-confdb-syntax-system-user-username-authentication-ssh-dsa>`

          * :ref:`\*\<dsa\><dev-confdb-syntax-system-user-username-authentication-ssh-dsa-dsa>`

* :ref:`interfaces<dev-confdb-syntax-interfaces>`

  * :ref:`\*\<interface\><dev-confdb-syntax-interfaces-interface>`

    * :ref:`meta<dev-confdb-syntax-interfaces-interface-meta>`

      * :ref:`profile<dev-confdb-syntax-interfaces-interface-meta-profile>`

        * :ref:`id<dev-confdb-syntax-interfaces-interface-meta-profile-id>`

          * :ref:`\<id\><dev-confdb-syntax-interfaces-interface-meta-profile-id-id>`

        * :ref:`name<dev-confdb-syntax-interfaces-interface-meta-profile-name>`

          * :ref:`\<name\><dev-confdb-syntax-interfaces-interface-meta-profile-name-name>`

      * :ref:`link<dev-confdb-syntax-interfaces-interface-meta-link>`

        * :ref:`\*\<link\><dev-confdb-syntax-interfaces-interface-meta-link-link>`

          * :ref:`object<dev-confdb-syntax-interfaces-interface-meta-link-link-object>`

            * :ref:`id<dev-confdb-syntax-interfaces-interface-meta-link-link-object-id>`

              * :ref:`\<object_id\><dev-confdb-syntax-interfaces-interface-meta-link-link-object-id-object_id>`

            * :ref:`name<dev-confdb-syntax-interfaces-interface-meta-link-link-object-name>`

              * :ref:`\<object_name\><dev-confdb-syntax-interfaces-interface-meta-link-link-object-name-object_name>`

            * :ref:`profile<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile>`

              * :ref:`id<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id>`

                * :ref:`\<id\><dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id-id>`

              * :ref:`name<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name>`

                * :ref:`\<name\><dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name-name>`

              * :ref:`level<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level>`

                * :ref:`\<level\><dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level-level>`

          * :ref:`interface<dev-confdb-syntax-interfaces-interface-meta-link-link-interface>`

            * :ref:`\*\<remote_interface\><dev-confdb-syntax-interfaces-interface-meta-link-link-interface-remote_interface>`

    * :ref:`type<dev-confdb-syntax-interfaces-interface-type>`

      * :ref:`\<type\><dev-confdb-syntax-interfaces-interface-type-type>`

    * :ref:`description<dev-confdb-syntax-interfaces-interface-description>`

      * :ref:`\<description\><dev-confdb-syntax-interfaces-interface-description-description>`

    * :ref:`admin-status<dev-confdb-syntax-interfaces-interface-admin-status>`

      * :ref:`\<admin_status\><dev-confdb-syntax-interfaces-interface-admin-status-admin_status>`

    * :ref:`mtu<dev-confdb-syntax-interfaces-interface-mtu>`

      * :ref:`\<mtu\><dev-confdb-syntax-interfaces-interface-mtu-mtu>`

    * :ref:`speed<dev-confdb-syntax-interfaces-interface-speed>`

      * :ref:`\<speed\><dev-confdb-syntax-interfaces-interface-speed-speed>`

    * :ref:`duplex<dev-confdb-syntax-interfaces-interface-duplex>`

      * :ref:`\<duplex\><dev-confdb-syntax-interfaces-interface-duplex-duplex>`

    * :ref:`flow-control<dev-confdb-syntax-interfaces-interface-flow-control>`

      * :ref:`\<flow_control\><dev-confdb-syntax-interfaces-interface-flow-control-flow_control>`

    * :ref:`ethernet<dev-confdb-syntax-interfaces-interface-ethernet>`

      * :ref:`auto-negotiation<dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation>`

        * :ref:`\*\<mode\><dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation-mode>`

    * :ref:`storm-control<dev-confdb-syntax-interfaces-interface-storm-control>`

      * :ref:`broadcast<dev-confdb-syntax-interfaces-interface-storm-control-broadcast>`

        * :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level>`

          * :ref:`\<level\><dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level-level>`

      * :ref:`multicast<dev-confdb-syntax-interfaces-interface-storm-control-multicast>`

        * :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-multicast-level>`

          * :ref:`\<level\><dev-confdb-syntax-interfaces-interface-storm-control-multicast-level-level>`

      * :ref:`unicast<dev-confdb-syntax-interfaces-interface-storm-control-unicast>`

        * :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-unicast-level>`

          * :ref:`\<level\><dev-confdb-syntax-interfaces-interface-storm-control-unicast-level-level>`

* :ref:`protocols<dev-confdb-syntax-protocols>`

  * :ref:`ntp<dev-confdb-syntax-protocols-ntp>`

    * :ref:`\*\<name\><dev-confdb-syntax-protocols-ntp-name>`

      * :ref:`version<dev-confdb-syntax-protocols-ntp-name-version>`

        * :ref:`\<version\><dev-confdb-syntax-protocols-ntp-name-version-version>`

      * :ref:`address<dev-confdb-syntax-protocols-ntp-name-address>`

        * :ref:`\<address\><dev-confdb-syntax-protocols-ntp-name-address-address>`

      * :ref:`mode<dev-confdb-syntax-protocols-ntp-name-mode>`

        * :ref:`\<mode\><dev-confdb-syntax-protocols-ntp-name-mode-mode>`

      * :ref:`authentication<dev-confdb-syntax-protocols-ntp-name-authentication>`

        * :ref:`type<dev-confdb-syntax-protocols-ntp-name-authentication-type>`

          * :ref:`\<auth_type\><dev-confdb-syntax-protocols-ntp-name-authentication-type-auth_type>`

        * :ref:`key<dev-confdb-syntax-protocols-ntp-name-authentication-key>`

          * :ref:`\<key\><dev-confdb-syntax-protocols-ntp-name-authentication-key-key>`

      * :ref:`prefer<dev-confdb-syntax-protocols-ntp-name-prefer>`

      * :ref:`broadcast<dev-confdb-syntax-protocols-ntp-name-broadcast>`

        * :ref:`version<dev-confdb-syntax-protocols-ntp-name-broadcast-version>`

          * :ref:`\<version\><dev-confdb-syntax-protocols-ntp-name-broadcast-version-version>`

        * :ref:`address<dev-confdb-syntax-protocols-ntp-name-broadcast-address>`

          * :ref:`\<address\><dev-confdb-syntax-protocols-ntp-name-broadcast-address-address>`

        * :ref:`ttl<dev-confdb-syntax-protocols-ntp-name-broadcast-ttl>`

          * :ref:`\<ttl\><dev-confdb-syntax-protocols-ntp-name-broadcast-ttl-ttl>`

        * :ref:`authentication<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication>`

          * :ref:`type<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type>`

            * :ref:`\<auth_type\><dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type-auth_type>`

          * :ref:`key<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key>`

            * :ref:`\<key\><dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key-key>`

    * :ref:`boot-server<dev-confdb-syntax-protocols-ntp-boot-server>`

      * :ref:`\<boot_server\><dev-confdb-syntax-protocols-ntp-boot-server-boot_server>`

  * :ref:`cdp<dev-confdb-syntax-protocols-cdp>`

    * :ref:`interface<dev-confdb-syntax-protocols-cdp-interface>`

      * :ref:`\*\<interface\><dev-confdb-syntax-protocols-cdp-interface-interface>`

  * :ref:`lldp<dev-confdb-syntax-protocols-lldp>`

    * :ref:`interface<dev-confdb-syntax-protocols-lldp-interface>`

      * :ref:`\*\<interface\><dev-confdb-syntax-protocols-lldp-interface-interface>`

        * :ref:`admin-status<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status>`

          * :ref:`rx<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status-rx>`

          * :ref:`tx<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status-tx>`

  * :ref:`udld<dev-confdb-syntax-protocols-udld>`

    * :ref:`interface<dev-confdb-syntax-protocols-udld-interface>`

      * :ref:`\*\<interface\><dev-confdb-syntax-protocols-udld-interface-interface>`

  * :ref:`spanning-tree<dev-confdb-syntax-protocols-spanning-tree>`

    * :ref:`mode<dev-confdb-syntax-protocols-spanning-tree-mode>`

      * :ref:`\<mode\><dev-confdb-syntax-protocols-spanning-tree-mode-mode>`

    * :ref:`priority<dev-confdb-syntax-protocols-spanning-tree-priority>`

      * :ref:`\<priority\><dev-confdb-syntax-protocols-spanning-tree-priority-priority>`

    * :ref:`instance<dev-confdb-syntax-protocols-spanning-tree-instance>`

      * :ref:`\*\<instance\><dev-confdb-syntax-protocols-spanning-tree-instance-instance>`

        * :ref:`bridge-priority<dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority>`

          * :ref:`\<priority\><dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority-priority>`

    * :ref:`interface<dev-confdb-syntax-protocols-spanning-tree-interface>`

      * :ref:`\*\<interface\><dev-confdb-syntax-protocols-spanning-tree-interface-interface>`

        * :ref:`admin-status<dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status>`

          * :ref:`\<admin_status\><dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status-admin_status>`

        * :ref:`cost<dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost>`

          * :ref:`\<cost\><dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost-cost>`

        * :ref:`bpdu-filter<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter>`

          * :ref:`\<enabled\><dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter-enabled>`

        * :ref:`bpdu-guard<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard>`

          * :ref:`\<enabled\><dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard-enabled>`

        * :ref:`mode<dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode>`

          * :ref:`\<mode\><dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode-mode>`

  * :ref:`loop-detect<dev-confdb-syntax-protocols-loop-detect>`

    * :ref:`interface<dev-confdb-syntax-protocols-loop-detect-interface>`

      * :ref:`\*\<interface\><dev-confdb-syntax-protocols-loop-detect-interface-interface>`

* :ref:`virtual-router<dev-confdb-syntax-virtual-router>`

  * :ref:`\*\<vr\><dev-confdb-syntax-virtual-router-vr>`

    * :ref:`forwarding-instance<dev-confdb-syntax-virtual-router-vr-forwarding-instance>`

      * :ref:`\*\<instance\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`

        * :ref:`type<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type>`

          * :ref:`\<type\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type-type>`

        * :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description>`

          * :ref:`\<description\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description-description>`

        * :ref:`route-distinguisher<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher>`

          * :ref:`\<rd\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher-rd>`

        * :ref:`vrf-target<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target>`

          * :ref:`import<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import>`

            * :ref:`\*\<target\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import-target>`

          * :ref:`export<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export>`

            * :ref:`\*\<target\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export-target>`

        * :ref:`vpn-id<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id>`

          * :ref:`\<vpn_id\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id-vpn_id>`

        * :ref:`vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans>`

          * :ref:`\*\<vlan_id\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id>`

            * :ref:`name<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name>`

              * :ref:`\<name\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name-name>`

            * :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description>`

              * :ref:`\<description\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description-description>`

        * :ref:`interfaces<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces>`

          * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface>`

            * :ref:`unit<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit>`

              * :ref:`\*\<unit\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`

                * :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description>`

                  * :ref:`\<description\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description-description>`

                * :ref:`inet<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet>`

                  * :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address>`

                    * :ref:`\*\<address\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address-address>`

                * :ref:`inet6<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6>`

                  * :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address>`

                    * :ref:`\*\<address\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address-address>`

                * :ref:`iso<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-iso>`

                * :ref:`mpls<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-mpls>`

                * :ref:`bridge<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge>`

                  * :ref:`switchport<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport>`

                    * :ref:`untagged<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged>`

                      * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged-vlan_filter>`

                    * :ref:`native<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native>`

                      * :ref:`\<vlan_id\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native-vlan_id>`

                    * :ref:`tagged<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged>`

                      * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged-vlan_filter>`

                  * :ref:`port-security<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security>`

                    * :ref:`max-mac-count<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count>`

                      * :ref:`\<limit\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count-limit>`

                  * :ref:`\*\<num\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`

                    * :ref:`stack<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack>`

                      * :ref:`\<stack\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack-stack>`

                    * :ref:`outer_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans>`

                      * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans-vlan_filter>`

                    * :ref:`inner_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans>`

                      * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans-vlan_filter>`

                    * :ref:`\*\<op_num\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num>`

                      * :ref:`\<op\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op>`

                        * :ref:`\<vlan\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op-vlan>`

                  * :ref:`\*\<num\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`

                    * :ref:`stack<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack>`

                      * :ref:`\<stack\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack-stack>`

                    * :ref:`outer_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans>`

                      * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans-vlan_filter>`

                    * :ref:`inner_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans>`

                      * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans-vlan_filter>`

                    * :ref:`\*\<op_num\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num>`

                      * :ref:`\<op\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op>`

                        * :ref:`\<vlan\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op-vlan>`

                  * :ref:`dynamic_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans>`

                    * :ref:`\*\<vlan_filter\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter>`

                      * :ref:`service<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service>`

                        * :ref:`\<service\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service-service>`

        * :ref:`route<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route>`

          * :ref:`inet<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet>`

            * :ref:`static<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static>`

              * :ref:`\<route\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route>`

                * :ref:`next-hop<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop>`

                  * :ref:`\*\<next_hop\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop-next_hop>`

                * :ref:`discard<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-discard>`

          * :ref:`inet6<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6>`

            * :ref:`static<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static>`

              * :ref:`\<route\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route>`

                * :ref:`next-hop<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop>`

                  * :ref:`\*\<next_hop\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop-next_hop>`

        * :ref:`protocols<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`

          * :ref:`telnet<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-telnet>`

          * :ref:`ssh<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ssh>`

          * :ref:`http<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-http>`

          * :ref:`https<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-https>`

          * :ref:`snmp<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp>`

            * :ref:`community<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community>`

              * :ref:`\*\<community\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community>`

                * :ref:`level<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level>`

                  * :ref:`\<level\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level-level>`

            * :ref:`trap<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap>`

              * :ref:`community<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community>`

                * :ref:`\*\<community\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community>`

                  * :ref:`host<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host>`

                    * :ref:`\*\<address\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host-address>`

          * :ref:`isis<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis>`

            * :ref:`area<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area>`

              * :ref:`\*\<area\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area-area>`

            * :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface>`

              * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface>`

                * :ref:`level<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level>`

                  * :ref:`\*\<level\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level-level>`

          * :ref:`ospf<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf>`

            * :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface>`

              * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface-interface>`

          * :ref:`ldp<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp>`

            * :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface>`

              * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface-interface>`

          * :ref:`rsvp<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp>`

            * :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface>`

              * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface-interface>`

          * :ref:`pim<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim>`

            * :ref:`mode<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode>`

              * :ref:`\<mode\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode-mode>`

            * :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface>`

              * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface-interface>`

          * :ref:`igmp-snooping<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping>`

            * :ref:`vlan<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan>`

              * :ref:`\*\<vlan\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan>`

                * :ref:`version<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version>`

                  * :ref:`\<version\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version-version>`

                * :ref:`immediate-leave<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-immediate-leave>`

                * :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface>`

                  * :ref:`\*\<interface\><dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface>`

                    * :ref:`multicast-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface-multicast-router>`

* :ref:`media<dev-confdb-syntax-media>`

  * :ref:`sources<dev-confdb-syntax-media-sources>`

    * :ref:`video<dev-confdb-syntax-media-sources-video>`

      * :ref:`\*\<name\><dev-confdb-syntax-media-sources-video-name>`

        * :ref:`settings<dev-confdb-syntax-media-sources-video-name-settings>`

          * :ref:`brightness<dev-confdb-syntax-media-sources-video-name-settings-brightness>`

            * :ref:`\<brightness\><dev-confdb-syntax-media-sources-video-name-settings-brightness-brightness>`

          * :ref:`saturation<dev-confdb-syntax-media-sources-video-name-settings-saturation>`

            * :ref:`\<saturation\><dev-confdb-syntax-media-sources-video-name-settings-saturation-saturation>`

          * :ref:`contrast<dev-confdb-syntax-media-sources-video-name-settings-contrast>`

            * :ref:`\<contrast\><dev-confdb-syntax-media-sources-video-name-settings-contrast-contrast>`

          * :ref:`sharpness<dev-confdb-syntax-media-sources-video-name-settings-sharpness>`

            * :ref:`\<sharpness\><dev-confdb-syntax-media-sources-video-name-settings-sharpness-sharpness>`

          * :ref:`white-balance<dev-confdb-syntax-media-sources-video-name-settings-white-balance>`

            * :ref:`admin-status<dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status>`

              * :ref:`\<admin_status\><dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status-admin_status>`

            * :ref:`auto<dev-confdb-syntax-media-sources-video-name-settings-white-balance-auto>`

            * :ref:`cr-gain<dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain>`

              * :ref:`\<cr_gain\><dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain-cr_gain>`

            * :ref:`gb-gain<dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain>`

              * :ref:`\<gb_gain\><dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain-gb_gain>`

          * :ref:`black-light-compensation<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation>`

            * :ref:`admin-status<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status>`

              * :ref:`\<admin_status\><dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status-admin_status>`

          * :ref:`wide-dynamic-range<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range>`

            * :ref:`admin-status<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status>`

              * :ref:`\<admin_status\><dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status-admin_status>`

            * :ref:`level<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level>`

              * :ref:`\<level\><dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level-level>`

    * :ref:`audio<dev-confdb-syntax-media-sources-audio>`

      * :ref:`\*\<name\><dev-confdb-syntax-media-sources-audio-name>`

        * :ref:`source<dev-confdb-syntax-media-sources-audio-name-source>`

          * :ref:`\<source\><dev-confdb-syntax-media-sources-audio-name-source-source>`

        * :ref:`settings<dev-confdb-syntax-media-sources-audio-name-settings>`

          * :ref:`volume<dev-confdb-syntax-media-sources-audio-name-settings-volume>`

            * :ref:`\<volume\><dev-confdb-syntax-media-sources-audio-name-settings-volume-volume>`

          * :ref:`noise-reduction<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction>`

            * :ref:`admin-status<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status>`

              * :ref:`\<admin_status\><dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status-admin_status>`

  * :ref:`streams<dev-confdb-syntax-media-streams>`

    * :ref:`\*\<name\><dev-confdb-syntax-media-streams-name>`

      * :ref:`rtsp-path<dev-confdb-syntax-media-streams-name-rtsp-path>`

        * :ref:`\<path\><dev-confdb-syntax-media-streams-name-rtsp-path-path>`

      * :ref:`settings<dev-confdb-syntax-media-streams-name-settings>`

        * :ref:`video<dev-confdb-syntax-media-streams-name-settings-video>`

          * :ref:`admin-status<dev-confdb-syntax-media-streams-name-settings-video-admin-status>`

            * :ref:`\<admin_status\><dev-confdb-syntax-media-streams-name-settings-video-admin-status-admin_status>`

          * :ref:`resolution<dev-confdb-syntax-media-streams-name-settings-video-resolution>`

            * :ref:`width<dev-confdb-syntax-media-streams-name-settings-video-resolution-width>`

              * :ref:`\<width\><dev-confdb-syntax-media-streams-name-settings-video-resolution-width-width>`

            * :ref:`height<dev-confdb-syntax-media-streams-name-settings-video-resolution-height>`

              * :ref:`\<height\><dev-confdb-syntax-media-streams-name-settings-video-resolution-height-height>`

          * :ref:`codec<dev-confdb-syntax-media-streams-name-settings-video-codec>`

            * :ref:`mpeg4<dev-confdb-syntax-media-streams-name-settings-video-codec-mpeg4>`

            * :ref:`h264<dev-confdb-syntax-media-streams-name-settings-video-codec-h264>`

              * :ref:`profile<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile>`

                * :ref:`name<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name>`

                  * :ref:`\<profile\><dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name-profile>`

                * :ref:`id<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id>`

                  * :ref:`\<id\><dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id-id>`

                * :ref:`constraint-set<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set>`

                  * :ref:`\<constraints\><dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set-constraints>`

                * :ref:`gov-length<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length>`

                  * :ref:`\<gov_length\><dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length-gov_length>`

          * :ref:`rate-control<dev-confdb-syntax-media-streams-name-settings-video-rate-control>`

            * :ref:`min-framerate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate>`

              * :ref:`\<min_framerate\><dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate-min_framerate>`

            * :ref:`max-framerate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate>`

              * :ref:`\<max_framerate\><dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate-max_framerate>`

            * :ref:`mode<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode>`

              * :ref:`cbr<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr>`

                * :ref:`bitrate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate>`

                  * :ref:`\<bitrate\><dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate-bitrate>`

              * :ref:`vbr<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr>`

                * :ref:`max-bitrate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate>`

                  * :ref:`\<max_bitrate\><dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate-max_bitrate>`

        * :ref:`audio<dev-confdb-syntax-media-streams-name-settings-audio>`

          * :ref:`admin-status<dev-confdb-syntax-media-streams-name-settings-audio-admin-status>`

            * :ref:`\<admin_status\><dev-confdb-syntax-media-streams-name-settings-audio-admin-status-admin_status>`

          * :ref:`codec<dev-confdb-syntax-media-streams-name-settings-audio-codec>`

            * :ref:`\<codec\><dev-confdb-syntax-media-streams-name-settings-audio-codec-codec>`

          * :ref:`bitrate<dev-confdb-syntax-media-streams-name-settings-audio-bitrate>`

            * :ref:`\<bitrate\><dev-confdb-syntax-media-streams-name-settings-audio-bitrate-bitrate>`

          * :ref:`samplerate<dev-confdb-syntax-media-streams-name-settings-audio-samplerate>`

            * :ref:`\<samplerate\><dev-confdb-syntax-media-streams-name-settings-audio-samplerate-samplerate>`

        * :ref:`overlays<dev-confdb-syntax-media-streams-name-settings-overlays>`

          * :ref:`\<overlay_name\><dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name>`

            * :ref:`admin-status<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status>`

              * :ref:`\<admin_status\><dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status-admin_status>`

            * :ref:`position<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position>`

              * :ref:`x<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x>`

                * :ref:`\<x\><dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x-x>`

              * :ref:`y<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y>`

                * :ref:`\<y\><dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y-y>`

            * :ref:`text<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text>`

              * :ref:`\<text\><dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text-text>`

* :ref:`hints<dev-confdb-syntax-hints>`

  * :ref:`interfaces<dev-confdb-syntax-hints-interfaces>`

    * :ref:`defaults<dev-confdb-syntax-hints-interfaces-defaults>`

      * :ref:`admin-status<dev-confdb-syntax-hints-interfaces-defaults-admin-status>`

        * :ref:`\<admin_status\><dev-confdb-syntax-hints-interfaces-defaults-admin-status-admin_status>`

  * :ref:`protocols<dev-confdb-syntax-hints-protocols>`

    * :ref:`lldp<dev-confdb-syntax-hints-protocols-lldp>`

      * :ref:`status<dev-confdb-syntax-hints-protocols-lldp-status>`

        * :ref:`\<status\><dev-confdb-syntax-hints-protocols-lldp-status-status>`

      * :ref:`interface<dev-confdb-syntax-hints-protocols-lldp-interface>`

        * :ref:`\*\<interface\><dev-confdb-syntax-hints-protocols-lldp-interface-interface>`

          * :ref:`off<dev-confdb-syntax-hints-protocols-lldp-interface-interface-off>`

    * :ref:`cdp<dev-confdb-syntax-hints-protocols-cdp>`

      * :ref:`status<dev-confdb-syntax-hints-protocols-cdp-status>`

        * :ref:`\<status\><dev-confdb-syntax-hints-protocols-cdp-status-status>`

      * :ref:`interface<dev-confdb-syntax-hints-protocols-cdp-interface>`

        * :ref:`\*\<interface\><dev-confdb-syntax-hints-protocols-cdp-interface-interface>`

          * :ref:`off<dev-confdb-syntax-hints-protocols-cdp-interface-interface-off>`

    * :ref:`spanning-tree<dev-confdb-syntax-hints-protocols-spanning-tree>`

      * :ref:`status<dev-confdb-syntax-hints-protocols-spanning-tree-status>`

        * :ref:`\<status\><dev-confdb-syntax-hints-protocols-spanning-tree-status-status>`

      * :ref:`priority<dev-confdb-syntax-hints-protocols-spanning-tree-priority>`

        * :ref:`\<priority\><dev-confdb-syntax-hints-protocols-spanning-tree-priority-priority>`

      * :ref:`interface<dev-confdb-syntax-hints-protocols-spanning-tree-interface>`

        * :ref:`\*\<interface\><dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface>`

          * :ref:`off<dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface-off>`

    * :ref:`loop-detect<dev-confdb-syntax-hints-protocols-loop-detect>`

      * :ref:`status<dev-confdb-syntax-hints-protocols-loop-detect-status>`

        * :ref:`\<status\><dev-confdb-syntax-hints-protocols-loop-detect-status-status>`

      * :ref:`interface<dev-confdb-syntax-hints-protocols-loop-detect-interface>`

        * :ref:`\*\<interface\><dev-confdb-syntax-hints-protocols-loop-detect-interface-interface>`

          * :ref:`off<dev-confdb-syntax-hints-protocols-loop-detect-interface-interface-off>`

