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
                    stateId: "inv.interface-l1-grid",
                    store: me.store,
                    columns: [
                        {
                            xtype: "actioncolumn",
                            width: 25,
                            items: [
                                {
                                    tooltip: "Link/Unlink",
                                    scope: me,
                                    handler: me.onLink,
                                    disabled: !me.app.hasPermission("link"),
                                    getClass: function(col, meta, r) {
                                        if(r.get("link")) {
                                            return "icon_disconnect";
                                        } else {
                                            return "icon_connect";
                                        }
                                    }
                                }
                            ]
                        },
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
                            renderer: NOC.render.ClickableLookup("profile"),
                            onClick: me.onChangeProfile
                        },
                        {
                            text: "Project",
                            dataIndex: "project",
                            renderer: NOC.render.ClickableLookup("project"),
                            onClick: me.onChangeProject
                        },
                        {
                            text: "State",
                            dataIndex: "state",
                            renderer: NOC.render.ClickableLookup("state"),
                            onClick: me.onChangeState
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
                        listeners: {
                            scope: me,
                            cellclick: me.onCellClick
                        }
                    }
                }
            ]
        });
        me.callParent();
    },
    //
    onLink: function(grid, rowIndex, colIndex) {
        var me = this,
            r = me.store.getAt(rowIndex),
            link = r.get("link");
        if(link) {
            me.unlinkInterface(r.get("id"), r.get("name"));
        } else {
            me.linkInterface(r.get("id"), r.get("name"));
        }
    },
    //
    unlinkInterface: function(ifaceId, ifaceName) {
        var me = this;
        Ext.Msg.show({
            title: "Unlink interface",
            msg: Ext.String.format("Do you wish to unlink interface {0}?", ifaceName),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if (button == "yes") {
                    Ext.Ajax.request({
                        url: "/inv/interface/unlink/" + ifaceId + "/",
                        method: "POST",
                        scope: me,
                        success: function(response) {
                            var me = this,
                                data = Ext.decode(response.responseText);
                            if(data.status) {
                                me.app.loadInterfaces();
                            } else {
                                NOC.error(data.message);
                            }
                        }
                    });
                }
            }
        });
    },
    //
    linkInterface: function(ifaceId, ifaceName) {
        var me = this;
        Ext.create("NOC.inv.interface.LinkForm", {
            title: Ext.String.format("Link {0} with", ifaceName),
            app: me.app,
            ifaceId: ifaceId
        });
    },
    //
    onCellClick: function(view, cell, cellIndex, record, row,
                          rowIndex, e) {
        var me = this;
        if(e.target.tagName == "A") {
            var header = view.panel.headerCt.getHeaderAtIndex(cellIndex);
            if(header.onClick) {
                header.onClick.apply(me, [record]);
            }
        }
    },
    //
    onChangeProfile: function(record) {
        var me = this;
        Ext.create("NOC.inv.interface.ChangeInterfaceProfileForm", {
            app: me,
            record: record
        });
    },
    //
    onChangeProject: function(record) {
        var me = this;
        Ext.create("NOC.inv.interface.ChangeInterfaceProjectForm", {
            app: me,
            record: record
        });
    },
    //
    onChangeState: function(record) {
        var me = this;
        Ext.create("NOC.inv.interface.ChangeInterfaceStateForm", {
            app: me,
            record: record
        });
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
