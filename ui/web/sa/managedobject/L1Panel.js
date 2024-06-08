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
        "NOC.core.StateField",
        "NOC.core.ComboBox",
    ],
    title: __("Physical"),
    closable: false,
    layout: "fit",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        me.gridPlugins = [];

        if(NOC.hasPermission("change_interface")) {
            me.gridPlugins.push(
                Ext.create("Ext.grid.plugin.RowEditing", {
                    clicksToEdit: 2,
                    listeners: {
                        scope: me,
                        edit: me.onEdit,
                        canceledit: me.onCancelEdit
                    }
                })
            );
        }

        me.addInterfaceButton = Ext.create("Ext.button.Button", {
            text: __("Add Interface"),
            glyph: NOC.glyph.plus,
            scope: me,
            disabled: !NOC.hasPermission("sa:managedobject:change_interface"),
            handler: me.onAddInterface
        });

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
                            text: __("Name"),
                            dataIndex: "name",
                            editor: {
                                xtype: 'textfield',
                                allowBlank: false
                            }
                        },
                        {
                            text: __("Status"),
                            dataIndex: "status",
                            width: 100
                        },
                        {
                            text: __("Metrics"),
                            dataIndex: "metrics",
                            width: 100
                        },
                        {
                            text: __("MAC"),
                            dataIndex: "mac",
                            width: 120
                        },
                        {
                            text: __("LAG"),
                            dataIndex: "lag"
                        },
                        {
                            text: __("Link"),
                            dataIndex: "link",
                            renderer: function(value, meta, record) {
                                var v = value ? value.label : "...";
                                return "<a href='#' class='noc-clickable-cell' title='Click to change...'>" + v + "</a>";
                            },
                            onClick: me.onLinkClick
                        },
                        {
                            text: __("Profile"),
                            dataIndex: "profile",
                            renderer: NOC.render.Lookup("profile"),
                            editor: {
                                xtype: "core.combo",
                                restUrl: "/inv/interfaceprofile/lookup/",
                            }
                        },
                        {
                            text: __("Project"),
                            dataIndex: "project",
                            renderer: NOC.render.Lookup("project"),
                            editor: {
                                xtype: "core.combo",
                                restUrl: "/project/project/lookup/",
                            },
                        },
                        {
                            text: __("State"),
                            dataIndex: "state",
                            editor: {
                                xtype: "statefield",
                                restUrl: "/inv/interface/"
                            },
                            renderer: NOC.render.Lookup("state"),
                        },
                        {
                            text: __("Protocols"),
                            dataIndex: "enabled_protocols"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            flex: 1,
                            editor: {
                                xtype: 'textfield'
                            }
                        },
                        {
                            text: __("ifIndex"),
                            dataIndex: "ifindex",
                            hidden: true,
                            width: 50
                        },
                        {
                            xtype: 'glyphactioncolumn',
                            items: [{
                                disabled: !NOC.hasPermission("sa:managedobject:change_interface"),
                                glyph: NOC.glyph.minus_circle,
                                scope: me,
                                handler: me.onRemoveInterface
                            }]
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: "toolbar",
                            dock: "top",
                            items: [
                                me.addInterfaceButton
                            ]
                        }
                    ],
                    viewConfig: {
                        getRowClass: Ext.bind(me.getRowClass, me),
                        listeners: {
                            scope: me,
                            cellclick: me.onCellClick
                        }
                    },
                    plugins: me.gridPlugins
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
            r = e.record,
            data = {
                profile: r.get("profile"),
                project: r.get("project"),
                state: r.get("state"),
                description: r.get("description")
            },
            isNewRecord = Ext.isEmpty(e.originalValues.name);
        if(isNewRecord) {
            data["name"] = r.get("name");
        } else {
            data["id"] = r.get("id");
        }
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.app.currentRecord.get("id") + "/interface/",
            method: "POST",
            jsonData: data,
            scope: me,
            success: function() {
                me.app.onRefresh();
                if(isNewRecord) {
                    NOC.info(__("Created interface: ") + r.get("name"));
                } else {
                    NOC.info(__("Saved"));
                }
                // @todo: Set tab
            },
            failure: function() {
                NOC.error(__("Failed to set data"));
            }
        });
    },

    onLinkClick: function(record) {
        var me = this;
        Ext.create("NOC.sa.managedobject.LinkForm", {
            title: Ext.String.format(__("Link") + " {0} " + __("with"), record.get("name")),
            app: me.app,
            ifaceId: record.get("id"),
            ifName: record.get("name"),
            isLinked: !!record.get("link"),
            linkId: record.get("link") ? record.get("link").id : null
        });
    },

    onCellClick: function(view, cell, cellIndex, record, row, rowIndex, e) {
        var me = this;
        if(e.target.tagName === "A") {
            var header = view.panel.headerCt.getHeaderAtIndex(cellIndex);
            if(header.onClick) {
                header.onClick.apply(me, [record]);
            }
        }
    },

    onRemoveInterface: function(grid, rowIndex) {
        var me = this,
            rec = grid.getStore().getAt(rowIndex);
        console.log(me.app.currentRecord.get("id"));
        Ext.Msg.show({
            title: __("Remove interface"),
            msg: __("Would you like remove interface ") + rec.get("name"),
            buttons: Ext.Msg.YESNO,
            modal: true,
            fn: function(button) {
                if(button === "yes") {
                    me.removeInterface(me.app.currentRecord.get("id"), rec.get("id"));
                }
            }
        })
    },

    onAddInterface: function() {
        var me = this,
            editPlugin = me.gridPlugins[0];
        editPlugin.cancelEdit();
        me.store.insert(0, {});
        editPlugin.startEdit(0, 0);
    },

    onCancelEdit: function(editor, context) {
        if(context.record.phantom) {
            context.grid.store.removeAt(context.rowIdx);
        }
    },

    removeInterface: function(objectId, interfaceId) {
        var me = this;
        Ext.Ajax.request({
            url: "/sa/managedobject/" + objectId + "/interface/" + interfaceId + "/",
            method: "DELETE",
            success: function(response) {
                me.app.onRefresh();
                NOC.info(__("Deleted"));
            },
            failure: function() {
                NOC.error(__("Failed to remove interface"));
            }
        });
    }
});
