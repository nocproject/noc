//---------------------------------------------------------------------
// sa.managedobject L1 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.L1Panel");

Ext.define("NOC.sa.managedobject.L1Panel", {
    extend: "Ext.panel.Panel",
    uses: [],
    title: "Physical",
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
                    stateId: "sa.managedobject-l1-grid",
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
                            text: "LAG",
                            dataIndex: "lag"
                        },
                        {
                            text: "Link",
                            dataIndex: "link",
                            renderer: function(v) {
                                if(v) {
                                    return v.label;
                                } else {
                                    return "";
                                }
                            }
                        },
                        {
                            text: "Profile",
                            dataIndex: "profile",
                            renderer: NOC.render.Lookup("profile")
                        },
                        {
                            text: "Project",
                            dataIndex: "project",
                            renderer: NOC.render.Lookup("project")
                        },
                        {
                            text: "State",
                            dataIndex: "state",
                            renderer: NOC.render.Lookup("state")
                        },
                        {
                            text: "VC Domain",
                            dataIndex: "vc_domain",
                            renderer: NOC.render.Lookup("vc_domain")
                        },
                        {
                            text: "Protocols",
                            dataIndex: "enabled_protocols"
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
                    ],
                    viewConfig: {
                        getRowClass: Ext.bind(me.getRowClass, me),
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
