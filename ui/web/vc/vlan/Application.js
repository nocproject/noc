//---------------------------------------------------------------------
// vc.vlan application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlan.Application");

Ext.define("NOC.vc.vlan.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vlan.Model",
        "NOC.vc.vlanprofile.LookupField",
        "NOC.inv.networksegment.LookupField",
        "NOC.project.project.LookupField",
        "NOC.vc.vpn.LookupField",
        "NOC.vc.vlan.LookupField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.vc.vlan.Model",
    search: true,
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Segment"),
                    dataIndex: "segment",
                    width: 150,
                    renderer: NOC.render.Lookup("segment")
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("State"),
                    dataIndex: "state",
                    width: 150,
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("VLAN"),
                    dataIndex: "vlan",
                    width: 75
                },
                {
                    text: __("Translation"),
                    dataIndex: "translation_rule",
                    width: 50
                },
                {
                    text: __("Parent"),
                    dataIndex: "parent",
                    flex: 1,
                    renderer: NOC.render.Lookup("parent")
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "profile",
                    xtype: "vc.vlanprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "vlan",
                    xtype: "numberfield",
                    fieldLabel: __("VLAN"),
                    allowBlank: false,
                    uiStyle: "small",
                    minValue: 1,
                    maxValue: 4095
                },
                {
                    name: "segment",
                    xtype: "inv.networksegment.LookupField",
                    fieldLabel: __("Segment"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: false
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: __("Project"),
                    allowBlank: true
                },
                {
                    name: "vpn",
                    xtype: "vc.vpn.LookupField",
                    fieldLabel: __("VPN"),
                    allowBlank: true
                },
                {
                    name: "vni",
                    xtype: "numberfield",
                    fieldLabel: __("VNI"),
                    allowBlank: true,
                    minValue: 0,
                    maxValue: (1 << 24) - 1
                },
                {
                    name: "translation_rule",
                    xtype: "combobox",
                    fieldLabel: __("Translation Rule"),
                    allowBlank: true,
                    store: [
                        ["map", "map"],
                        ["push", "push"]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "parent",
                    xtype: "vc.vlan.LookupField",
                    fieldLabel: __("Parent"),
                    allowBlank: true
                },
                {
                    name: "apply_translation",
                    xtype: "checkbox",
                    boxLabel: __("Apply Translation")
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Discovery"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "first_discovered",
                            xtype: "displayfield",
                            fieldLabel: __("Discovered"),
                            allowBlank: true
                        },
                        {
                            name: "last_seen",
                            xtype: "displayfield",
                            fieldLabel: __("Last Seen"),
                            allowBlank: true
                        },
                        {
                            name: "expired",
                            xtype: "displayfield",
                            fieldLabel: __("Expired"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ],
            formToolbar: [
                {
                    itemId: "interfaces",
                    text: __("VLAN Interfaces"),
                    glyph: NOC.glyph.list,
                    tooltip: __("Show VLAN interfaces"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onVLANInterfaces
                }
            ]
        });

        me.ITEM_VLAN_INTERFACES = me.registerItem(
            Ext.create("NOC.core.TemplatePreview", {
                app: me,
                previewName: new Ext.XTemplate('Interfaces in VLAN {name} ({segment__label} VLAN {vlan})'),
                template: new Ext.XTemplate(
                    '<div class="noc-tp">\n' +
                    '    <table class="noc-report">\n' +
                    '        <!-- Untagged interfaces -->\n' +
                    '        <tpl if="interfaces.untagged.length">\n' +
                    '        <tr><th colspan="2">Untagged interfaces</th>\n' +
                    '            <tpl foreach="interfaces.untagged">\n' +
                    '        <tr>\n' +
                    '            <td style="width: 200px">{managed_object_name}</td>\n' +
                    '            <td>\n' +
                    '                <tpl foreach="interfaces">{name}, </tpl>\n' +
                    '            </td>\n' +
                    '        </tr>\n' +
                    '        </tpl>\n' +
                    '        </tpl>\n' +
                    '        <!-- Tagged interfaces -->\n' +
                    '        <tpl if="interfaces.tagged.length">\n' +
                    '        <tr><th colspan="2">Tagged interfaces</th>\n' +
                    '            <tpl foreach="interfaces.tagged">\n' +
                    '        <tr>\n' +
                    '            <td style="width: 200px">{managed_object_name}</td>\n' +
                    '            <td>\n' +
                    '                <tpl foreach="interfaces">{name}, </tpl>\n' +
                    '            </td>\n' +
                    '        </tr>\n' +
                    '        </tpl>\n' +
                    '        </tpl>\n' +
                    '        <!-- L3 interfaces -->\n' +
                    '        <tpl if="interfaces.l3.length">\n' +
                    '        <tr><th colspan="2">L3 interfaces</th>\n' +
                    '            <tpl foreach="interfaces.l3">\n' +
                    '        <tr>\n' +
                    '            <td style="width: 200px">{managed_object_name}</td>\n' +
                    '            <td>\n' +
                    '                <tpl foreach="interfaces">\n' +
                    '                {ipv4_addresses}\n' +
                    '                {ipv6_addresses}\n' +
                    '                </tpl>\n' +
                    '            </td>\n' +
                    '        </tr>\n' +
                    '        </tpl>\n' +
                    '        </tpl>\n' +
                    '    </table>\n' +
                    '</div>')
            })
        );
        me.callParent();
    },
    
    // Show interfaces window
    showVLANInterfaces: function(record) {
        var me = this;
        Ext.Ajax.request({
            url: "/vc/vlan/" + record.get("id") + "/interfaces/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(!r.tagged && !r.untagged && !r.l3) {
                    NOC.info(__("No interfaces found"));
                } else {
                    var item = me.showItem(me.ITEM_VLAN_INTERFACES);
                    item.preview(record, {interfaces: r});
                }
            },
            failure: function() {
                NOC.error(__("Failed to get interfaces"));
            }
        });
    },

    onVLANInterfaces: function() {
        var me = this;
        me.showVLANInterfaces(me.currentRecord);
    },
    //
    onInterfacesCellClick: function(record) {
        var me = this;
        me.showVLANInterfaces(record);
    }
});
