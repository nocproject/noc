//---------------------------------------------------------------------
// sa.managedobject L1 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.L1Panel");

Ext.define("NOC.sa.managedobject.L1Panel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.vc.vcdomain.LookupField",
        "NOC.project.project.LookupField",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.main.resourcestate.LookupField"
    ],
    title: "Physical",
    closable: false,
    layout: "fit",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this,
            gridPlugins = [];

        if(NOC.hasPermission("change_interface")) {
            gridPlugins.push(
                Ext.create("Ext.grid.plugin.RowEditing", {
                    clicksToEdit: 2,
                    listeners: {
                        scope: me,
                        edit: me.onEdit
                    }
                })
            );
        }

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
                            renderer: NOC.render.Lookup("profile"),
                            editor: "inv.interfaceprofile.LookupField"
                        },
                        {
                            text: "Project",
                            dataIndex: "project",
                            renderer: NOC.render.Lookup("project"),
                            editor: "project.project.LookupField"
                        },
                        {
                            text: "State",
                            dataIndex: "state",
                            renderer: NOC.render.Lookup("state"),
                            editor: "main.resourcestate.LookupField"
                        },
                        {
                            text: "VC Domain",
                            dataIndex: "vc_domain",
                            renderer: NOC.render.Lookup("vc_domain"),
                            editor: "vc.vcdomain.LookupField"
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
                        getRowClass: Ext.bind(me.getRowClass, me)
                    },
                    plugins: gridPlugins,
                    listeners: {
                        scope: me,
                        select: function(panel, record) {
                            me.app.metricsCurrentRecord = record;
                            me.app.metricsButton.setDisabled(false);
                        }
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
    },
    //
    onEdit: function(editor, e) {
        var me = this,
            r = e.record;
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.app.currentRecord.get("id") + "/interface/",
            method: "POST",
            jsonData: {
                "id": r.get("id"),
                "profile": r.get("profile"),
                "project": r.get("project"),
                "state": r.get("state"),
                "vc_domain": r.get("vc_domain")
            },
            scope: me,
            success: function(response) {
                me.app.onRefresh();
                // @todo: Set tab
            },
            failure: function() {
                NOC.error("Failed to set data");
            }
        });
    }
});
