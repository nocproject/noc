//---------------------------------------------------------------------
// sa.managedobject L3 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.L3Panel");

Ext.define("NOC.sa.managedobject.L3Panel", {
    extend: "Ext.panel.Panel",
    uses: [],
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
                    stateId: "sa.managedobject-L3-grid",
                    store: me.store,
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "VRF",
                            dataIndex: "vrf"
                        },
                        {
                            text: "IP",
                            dataIndex: "ip"
                        },
                        {
                            text: "IPv4",
                            dataIndex: "ipv4_addresses",
                            hidden: true
                        },
                        {
                            text: "IPv6",
                            dataIndex: "ipv6_addresses",
                            hidden: true
                        },
                        {
                            text: "Protocols",
                            dataIndex: "enabled_protocols"
                        },
                        {
                            text: "VLAN",
                            dataIndex: "vlan"
                        },
                        {
                            text: "MAC",
                            dataIndex: "mac"
                        },
                        {
                            text: "Description",
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
