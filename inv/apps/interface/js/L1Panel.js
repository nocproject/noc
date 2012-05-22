//---------------------------------------------------------------------
// inv.interface L1 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L1Panel");

Ext.define("NOC.inv.interface.L1Panel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "Physical",
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
                    stateId: "inv.interface-l1-grid",
                    store: me.store,
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "MAC",
                            dataIndex: "mac"
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            flex: 1
                        },
                        {
                            text: "ifIndex",
                            dataIndex: "ifindex",
                            hidden: true
                        }
                     ]
                }
            ]
        });
        me.callParent();
    }
});
