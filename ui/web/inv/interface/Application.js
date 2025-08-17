//---------------------------------------------------------------------
// inv.interface application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.Application");

Ext.define("NOC.inv.interface.Application", {
    extend: "NOC.core.ModelApplication",
    reference: "invInterface",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.core.StateField",
        "NOC.inv.interface.LinkForm",
        "NOC.inv.interface.MACForm",
        "NOC.inv.interface.Model",
        "NOC.inv.interface.type.LookupField",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.project.project.LookupField",
        "NOC.sa.service.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.vc.l2domain.LookupField",
        "Ext.ux.grid.SubTable",
    ],
    model: "NOC.inv.interface.Model",
    search: true,

    initComponent: function() {
        var me = this,
            subInterfaceHeader = new Ext.XTemplate(
                '<th class="' + Ext.baseCSSPrefix + 'grid-subtable-header">{.}</th>',
            ),
            subInterfaceCellStringValue = new Ext.XTemplate(
                '<td class="' + Ext.baseCSSPrefix + 'grid-subtable-cell"><div class="'
                + Ext.baseCSSPrefix + 'grid-cell-inner">{.}</div></td>'),
            subInterfaceCellArrayValue = new Ext.XTemplate(
                '<td class="' + Ext.baseCSSPrefix + 'grid-subtable-cell">',
                '<tpl for=".">',
                '<div class="' + Ext.baseCSSPrefix + 'grid-cell-inner">{.}</div>',
                '</tpl>',
                '</td>'
            );

        Ext.apply(me, {
            columns: [
                {
                    xtype: "glyphactioncolumn",
                    itemId: 'show_MAC_action',
                    width: 25,
                    items: [
                        {
                            scope: me,
                            tooltip: __("Show MACs"),
                            glyph: NOC.glyph.play,
                            handler: me.showMAC,
                            disabled: !me.permissions.get_mac,
                        }
                    ],
                },
                {
                    xtype: "glyphactioncolumn",
                    width: 25,
                    renderer: function(val, metadata, record) {
                        if(record.get("link")) {
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
                            disabled: !me.permissions.link
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
                    renderer: NOC.render.Lookup("link"),
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    renderer: NOC.render.Lookup("profile"),
                    editor: "inv.interfaceprofile.LookupField"
                },
                {
                    text: __("Project"),
                    dataIndex: "project",
                    renderer: NOC.render.Lookup("project"),
                    editor: "project.project.LookupField"
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
                    text: __("Service"),
                    dataIndex: "service",
                    renderer: NOC.render.Lookup("service"),
                    editor: "sa.service.LookupField"
                },
                {
                    text: __("Protocols"),
                    dataIndex: "enabled_protocols"
                },
                {
                    text: __("Caps"),
                    dataIndex: "caps",
                    renderer: function(value, meta, record){
                        var app = this.up("[reference=invInterface]");
                        return app.renderArrayValue(value, "label");
                    },
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 200
                },
                {
                    text: __("ifIndex"),
                    dataIndex: "ifindex",
                    hidden: false
                }
            ],
            additions_plugins: [
                {
                    ptype: "subtable",
                    association: "subinterfaces",
                    headerWidth: 32,
                    emptyText: __("No SubInterfaces"),
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name"
                        },
                        {
                            text: __("Untagged"),
                            dataIndex: "untagged_vlan"
                        },
                        {
                            text: __("Tagged"),
                            dataIndex: "tagged_vlans"
                        },
                        {
                            text: __("L2 Domain"),
                            dataIndex: "l2_domain",
                            renderer: NOC.render.ObjectLookup("l2_domain"),
                        },
                        {
                            text: __("VFR"),
                            dataIndex: "vrf"
                        },
                        {
                            text: __("IPv4"),
                            dataIndex: "ipv4_addresses",
                            renderer: NOC.render.Join(",")
                        },
                        {
                            text: __("IPv6"),
                            dataIndex: "ipv6_addresses",
                            renderer: NOC.render.Join(",")
                        },
                        {
                            text: __("Project"),
                            dataIndex: "project",
                            renderer: NOC.render.ObjectLookup("project"),
                            editor: "project.project.LookupField"
                        },
                        {
                            text: __("Service"),
                            dataIndex: "service",
                            renderer: NOC.render.ObjectLookup("service"),
                            editor: "sa.service.LookupField"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description"
                        },
                    ]
                }
            ],
        });
        me.callParent();
        if(NOC.hasPermission("change_interface")) {
            me.grid.addPlugin(
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
    },
    filters: [
        {
            title: __("By Object"),
            name: "managed_object",
            ftype: "lookup",
            lookup: "sa.managedobject"
        },
        {
            title: __("By Labels"),
            name: "labels",
            ftype: "label",
            filterProtected: false
        },
        {
            title: __("By Type"),
            name: "type",
            ftype: "lookup",
            lookup: "inv.interface.type"
        }
    ],
    renderArrayValue: function(value, label){
      if(Ext.isEmpty(value)) return "..."
      if(Ext.isArray(value)) return value.map(el => el[label]).join(", ");
      return value[label];

    },
    //
    onEdit: function(editor, e) {
        var me = this,
            r = e.record,
            data = {
                profile: r.get("profile"),
                project: r.get("project"),
                state: r.get("state"),
                l2_domain: r.get("l2_domain")
            },
            isNewRecord = Ext.isEmpty(e.originalValues.name);
        if(isNewRecord) {
            data["name"] = r.get("name");
        } else {
            data["id"] = r.get("id");
        }
        Ext.Ajax.request({
            url: "/inv/interface/" + r.get("id") + "/",
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
            },
            failure: function() {
                NOC.error(__("Failed to set data"));
            }
        });
    },
    //
    onCancelEdit: function(editor, context) {
        if(context.record.phantom) {
            context.grid.store.removeAt(context.rowIdx);
        }
    },
    //
    onLink: function(grid, rowIndex, colIndex) {
        var me = this,
            r = me.store.getAt(rowIndex),
            link = r.get("link");
        me.currentRecord = r;
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
                if(button === "yes") {
                    Ext.Ajax.request({
                        url: "/inv/interface/unlink/" + ifaceId + "/",
                        method: "POST",
                        scope: me,
                        success: function(response) {
                            var me = this,
                                data = Ext.decode(response.responseText);
                            if(data.status) {
                                me.currentRecord.set("link", null);
                                me.currentRecord.set("link_label", null);
                                me.grid.getStore().reload();
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
            app: me,
            ifaceId: ifaceId
        });
    },
    toggleLinkIcon: function(data) {
        var me = this;

        if(data) { // link
            me.currentRecord.set("link", data.link);
            me.grid.getStore().getById(me.currentRecord.id).set("link", data.link);
            me.currentRecord.set("link_label", data.link__label);
            me.grid.getStore().getById(me.currentRecord.id).set("link__label", data.link__label);
            // me.grid.getStore().reload();
            me.grid.getStore().sync();
        } else { // unlink
        }
    },
    //
    showMAC: function(grid, rowIndex, colIndex, item, event, record) {
        var me = this;

        me.currentRecord = record;
        NOC.mrt({
            scope: me,
            params: [
                {
                    id: me.currentRecord.get("managed_object"),
                    script: "get_mac_address_table",
                    args: {
                        interface: record.get("name")
                    }
                }
            ],
            errorMsg: __("Failed to get MACs"),
            cb: me.showMACForm
        });
    },
    //
    showMACForm: function(data, scope) {
        if(data) {
            Ext.create("NOC.inv.interface.MACForm", {
                objectId: scope.currentRecord.get("managed_object"),
                data: data,
                name: scope.currentRecord.get("name"),
                title: Ext.String.format("MACs on {0}",
                    scope.currentRecord.get("name"))
            });
        } else {
            NOC.error(__("Failed to get data"));
        }
    }
});
