//---------------------------------------------------------------------
// sa.managedobject LAG Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LAGPanel");

Ext.define("NOC.sa.managedobject.LAGPanel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "LAG",
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
                    stateId: "sa.managedobject-LAG-grid",
                    store: me.store,
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "Count",
                            dataIndex: "count"
                        },
                        {
                            text: "Members",
                            dataIndex: "members"
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
