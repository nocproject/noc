//---------------------------------------------------------------------
// MAC Log window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.MACLogForm");

Ext.define("NOC.inv.macdb.MACLogForm", {
    extend: "Ext.Window",
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    width: 700,
    height: 600,
    autoScroll: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("NOC.inv.macdb.MACLogStore");
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
                            text: "Timestamp",
                            dataIndex: "timestamp",
                            width: 160
                        },
                        {
                            text: "Mac",
                            dataIndex: "mac",
                            width: 110
                        },
                        {
                            text: "VC Domain",
                            dataIndex: "vc_domain",
                            flex: 1
                        },
                        {
                            text: "Vlan",
                            dataIndex: "vlan",
                            width: 40
                        },
                        {
                            text: "Managed Object",
                            dataIndex: "managed_object_name",
                            flex: 2
                        },
                        {
                            text: "Interface",     
                            dataIndex: "interface_name",
                            flex: 1
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
