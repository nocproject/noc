//---------------------------------------------------------------------
// vc.vc application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.Application");

Ext.define("NOC.vc.vc.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vc.Model",
        "NOC.main.style.LookupField",
        "NOC.main.resourcestate.LookupField",
        "NOC.project.project.LookupField",
        "NOC.vc.vcdomain.LookupField"
    ],
    model: "NOC.vc.vc.Model",
    search: true,
    rowClassField: "row_class",

    filters: [
        {
            title: __("By VC Domain"),
            name: "vc_domain",
            ftype: "lookup",
            lookup: "vc.vcdomain"
        },
        {
            title: __("By State"),
            name: "state",
            ftype: "lookup",
            lookup: "main.resourcestate"
        },
        {
            title: __("By Project"),
            name: "project",
            ftype: "lookup",
            lookup: "project.project"
        },
        {
            title: __("By VC Filter"),
            name: "l1",
            ftype: "vcfilter"
        },
        {
            title: __("By Tags"),
            name: "tags",
            ftype: "tag"
        },
        {
            title: __("By Style"),
            name: "style",
            ftype: "lookup",
            lookup: "main.style"
        }
    ],
    //
    initComponent: function() {
        var me = this;

        me.addFirstFreeForm = Ext.create("NOC.vc.vc.AddFirstFreeForm", {app: me});

        Ext.apply(me, {
            columns: [
                {
                    text: __("VC Domain"),
                    dataIndex: "vc_domain",
                    renderer: NOC.render.Lookup("vc_domain")
                },
                {
                    text: __("Name"),
                    dataIndex: "name"
                },
                {
                    text: __("State"),
                    dataIndex: "state",
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("Project"),
                    dataIndex: "project",
                    renderer: NOC.render.Lookup("project")
                },
                {
                    text: __("Label"),
                    dataIndex: "label",
                    width: 50,
                    sortable: false
                },
                {
                    text: __("L1"),
                    dataIndex: "l1",
                    width: 25,
                    hidden: true
                },
                {
                    text: __("L2"),
                    dataIndex: "l2",
                    width: 25,
                    hidden: true
                },
                {
                    text: __("Int."),
                    dataIndex: "interfaces_count",
                    width: 50,
                    sortable: false,
                    align: "right",
                    renderer: NOC.render.Clickable,
                    onClick: me.onInterfacesCellClick
                },
                {
                    text: __("Prefixes"),
                    dataIndex: "prefixes",
                    width: 100,
                    sortable: false
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    renderer: NOC.render.Tags
                }
            ],
            fields: [
                {
                    name: "vc_domain",
                    xtype: "vc.vcdomain.LookupField",
                    fieldLabel: __("VC Domain"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    regex: /^[a-zA-Z0-9_\-]+$/
                },
                {
                    name: "state",
                    xtype: "main.resourcestate.LookupField",
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
                    name: "l1",
                    xtype: "numberfield",
                    fieldLabel: __("L1"),
                    allowBlank: false
                },
                { // @todo: Auto-hide when VC domain does not support l2
                    name: "l2",
                    xtype: "numberfield",
                    fieldLabel: __("L2"),
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textfield",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ],

            gridToolbar: [
                {
                    itemId: "create_first",
                    text: __("Add First Free"),
                    glyph: NOC.glyph.plus_circle,
                    tooltip: __("Add first free VC"),
                    hasAccess: NOC.hasPermission("create"),
                    scope: me,
                    handler: me.onFirstNewRecord
                }
            ],
            formToolbar: [
                {
                    itemId: "interfaces",
                    text: __("VC Interfaces"),
                    glyph: NOC.glyph.list,
                    tooltip: __("Show VC interfaces"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onVCInterfaces
                }
            ]
        });
        me.ITEM_VC_INTERFACES = me.registerItem(
            Ext.create("NOC.core.TemplatePreview", {
                app: me,
                previewName: new Ext.XTemplate('Interfaces in VC {name} ({vc_domain__label} VLAN {l1})'),
                template: new Ext.XTemplate('<div class="noc-tp">\n    <table class="noc-report">\n        <!-- Untagged interfaces -->\n        <tpl if="interfaces.untagged.length">\n        <tr><th colspan="2">Untagged interfaces</th>\n            <tpl foreach="interfaces.untagged">\n        <tr>\n            <td style="width: 200px">{managed_object_name}</td>\n            <td>\n                <tpl foreach="interfaces">{name}, </tpl>\n            </td>\n        </tr>\n        </tpl>\n        </tpl>\n        <!-- Tagged interfaces -->\n        <tpl if="interfaces.tagged.length">\n        <tr><th colspan="2">Tagged interfaces</th>\n            <tpl foreach="interfaces.tagged">\n        <tr>\n            <td style="width: 200px">{managed_object_name}</td>\n            <td>\n                <tpl foreach="interfaces">{name}, </tpl>\n            </td>\n        </tr>\n        </tpl>\n        </tpl>\n        <!-- L3 interfaces -->\n        <tpl if="interfaces.l3.length">\n        <tr><th colspan="2">L3 interfaces</th>\n            <tpl foreach="interfaces.l3">\n        <tr>\n            <td style="width: 200px">{managed_object_name}</td>\n            <td>\n                <tpl foreach="interfaces">\n                {ipv4_addresses}\n                {ipv6_addresses}\n                </tpl>\n            </td>\n        </tr>\n        </tpl>\n        </tpl>\n    </table>\n</div>')
            })
        );
        me.callParent();
    },
    onFirstNewRecord: function() {
        var me = this;

        me.addFirstFreeForm.show();
    },
    // Show interfaces window
    showVCInterfaces: function(record) {
        var me = this;
        Ext.Ajax.request({
            url: "/vc/vc/" + record.get("id") + "/interfaces/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(!r.tagged && !r.untagged && !r.l3) {
                    NOC.info(__("No interfaces found"));
                } else {
                    var item = me.showItem(me.ITEM_VC_INTERFACES);
                    item.preview(record, {interfaces: r});
                }
            },
            failure: function() {
                NOC.error(__("Failed to get interfaces"));
            }
        });
    },

    onVCInterfaces: function() {
        var me = this;
        me.showVCInterfaces(me.currentRecord);
    },
    //
    onInterfacesCellClick: function(record) {
        var me = this;
        me.showVCInterfaces(record);
    }
});
