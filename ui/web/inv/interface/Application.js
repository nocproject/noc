//---------------------------------------------------------------------
// inv.interface application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.Application");

Ext.define("NOC.inv.interface.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.core.StateField",
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
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
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
                },
                // {
                //     ptype: 'rowexpander',
                //     rowBodyTpl: new Ext.XTemplate(
                //         '<tpl if="this.isNotEmptyArray(subinterfaces)">',
                //           '<table class="x-grid-item ' + Ext.baseCSSPrefix + 'grid-subtable"><tbody>',
                //           '<thead>',
                //             subInterfaceHeader.apply( __("Name")),
                //             subInterfaceHeader.apply( __("L2 Domain")),
                //             subInterfaceHeader.apply( __("VRF")),
                //             subInterfaceHeader.apply( __("IPv4")),
                //             subInterfaceHeader.apply( __("IPv6")),
                //             subInterfaceHeader.apply( __("Project")),
                //             subInterfaceHeader.apply( __("Service")),
                //             subInterfaceHeader.apply( __("Description")),
                //           '</thead>',
                //           '<tbody>',
                //           '<tpl for="subinterfaces">',
                //             '<tr>',
                //               subInterfaceCellStringValue.apply('{name}'),
                //               subInterfaceCellStringValue.apply('{l2_domain__label}'),
                //               subInterfaceCellStringValue.apply('{vrf}'),
                //               subInterfaceCellArrayValue.apply('{ipv4_addresses}'),
                //               subInterfaceCellArrayValue.apply('{ipv6_addresses}'),
                //               subInterfaceCellStringValue.apply('{project__label}'),
                //               subInterfaceCellStringValue.apply('{service__label}'),
                //               subInterfaceCellStringValue.apply('{description}'),
                //             '</tr>',
                //           '</tpl>',
                //           '</tbody></table>',
                //         '<tpl else>',
                //           '<p>' + __("No SubInterfaces") + '</p>',
                //         '</tpl>',
                //         {
                //             isNotEmptyArray: function(array) {
                //                 return array.length > 0;
                //             }
                //         })
                // }
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
    //
    onEdit: function(editor, e) {
        var me = this,
            r = e.record,
            data = {
                profile: r.get("profile"),
                project: r.get("project"),
                state: r.get("state"),
                vc_domain: r.get("vc_domain")
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
});
