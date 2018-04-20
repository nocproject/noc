//---------------------------------------------------------------------
// MAC Interfaces window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.MACForm");

Ext.define("NOC.inv.interface.MACForm", {
    extend: "Ext.Window",
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    width: 600,
    height: 400,
    autoScroll: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("NOC.inv.interface.MACStore");
        me.store.loadData(me.data);

        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    itemId: "grid",
                    store: me.store,
                    autoScroll: true,
                    layout: "fit",
                    columns: [
                        {
                            text: "Interface",
                            dataIndex: "interfaces"
                        },
                        {
                            text: "MAC",
                            dataIndex: "mac",
                            width: 110
                        },
                        {
                            text: "VLAN",
                            dataIndex: "vlan_id"
                        },
                        {
                            text: "type",
                            dataIndex: "type"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
