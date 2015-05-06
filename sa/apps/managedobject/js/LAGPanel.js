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
    rowClassField: "row_class",

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
                            text: "Profile",
                            dataIndex: "profile",
                            renderer: NOC.render.Lookup("profile"),
                            editor: "inv.interfaceprofile.LookupField"
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            flex: 1
                        }
                    ],
                    viewConfig: {
                        getRowClass: Ext.bind(me.getRowClass, me)
                    }
                }
            ]
        });
        me.callParent();
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store) {
        var me = this;
        if(me.rowClassField) {
            var c = record.get(me.rowClassField);
            if(c) {
                return c;
            } else {
                return "";
            }
        } else {
            return "";
        }
    }
});
