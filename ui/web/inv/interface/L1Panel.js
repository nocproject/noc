//---------------------------------------------------------------------
// inv.interface L1 Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L1Panel");

Ext.define("NOC.inv.interface.L1Panel", {
    extend: "Ext.panel.Panel",
    title: __("Physical"),
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
                            xtype: "glyphactioncolumn",
                            width: 25,
                            renderer: function (val, metadata, record) {
                                if (record.get("link")) {
                                    this.items[0].glyph = NOC.glyph.unlink;
                                    this.items[0].tooltip = __('Unlink');
                                } else {
                                    this.items[0].glyph = NOC.glyph.link;
                                    this.items[0].tooltip = __('Link');
                                }
                                metadata.style = 'cursor: pointer;';
                                return val;
                            },
                            items: [
                                {
                                    scope: me,
                                    handler: me.onLink,
                                    disabled: !me.app.hasPermission("link")
                                }
                            ]
                        },
                        {
                            text: __("Name"),
                            dataIndex: "name"
                        },
                        {
                            text: __("MAC"),
                            dataIndex: "mac"
                        },
                        {
                            text: __("LAG"),
                            dataIndex: "lag"
                        },
                        {
                            text: __("Link"),
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
                            text: __("Profile"),
                            dataIndex: "profile",
                            renderer: NOC.render.ClickableLookup("profile"),
                            onClick: me.onChangeProfile
                        },
                        {
                            text: __("Project"),
                            dataIndex: "project",
                            renderer: NOC.render.ClickableLookup("project"),
                            onClick: me.onChangeProject
                        },
                        {
                            text: __("State"),
                            dataIndex: "state",
                            renderer: NOC.render.ClickableLookup("state"),
                            onClick: me.onChangeState
                        },
                        {
                            text: __("VC Domain"),
                            dataIndex: "vc_domain",
                            renderer: NOC.render.ClickableLookup("vc_domain"),
                            onClick: me.onChangeVCDomain
                        },
                        {
                            text: __("Protocols"),
                            dataIndex: "enabled_protocols"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            flex: 1
                        },
                        {
                            text: __("ifIndex"),
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
            title: __("Unlink interface"),
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
            title: Ext.String.format(__("Link") + " {0} " + __("with"), ifaceName),
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
    onChangeVCDomain: function(record) {
        var me = this;
        Ext.create("NOC.inv.interface.ChangeInterfaceVCDomainForm", {
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
