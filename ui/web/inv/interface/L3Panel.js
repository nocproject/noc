//---------------------------------------------------------------------
// inv.interface L3 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L3Panel");

Ext.define("NOC.inv.interface.L3Panel", {
    extend: "Ext.panel.Panel",
    title: "L3",
    closable: false,
    layout: "fit",

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.interface-L3-grid",
                    store: me.store,
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name"
                        },
                        {
                            text: __("VRF"),
                            dataIndex: "vrf"
                        },
                        {
                            text: __("IP"),
                            dataIndex: "ip"
                        },
                        {
                            text: __("IPv4"),
                            dataIndex: "ipv4_addresses",
                            hidden: true
                        },
                        {
                            text: __("IPv6"),
                            dataIndex: "ipv6_addresses",
                            hidden: true
                        },
                        {
                            text: __("Protocols"),
                            dataIndex: "enabled_protocols"
                        },
                        {
                            text: __("VLAN"),
                            dataIndex: "vlan"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            flex: 1
                        }
                     ]
                }
            ]
        });
        me.callParent();
    }
});
