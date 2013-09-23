//---------------------------------------------------------------------
// sa.managedobject L2 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.L2Panel");

Ext.define("NOC.sa.managedobject.L2Panel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "Switchports",
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
                    stateId: "sa.managedobject-L2-grid",
                    store: me.store,
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "Untag.",
                            dataIndex: "untagged_vlan",
                            width: 50
                        },
                        {
                            text: "Tagged",
                            dataIndex: "tagged_vlans",
                            hidden: true
                        },
                        {
                            text: "Tagged (Ranges)",
                            dataIndex: "tagged_range"
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
