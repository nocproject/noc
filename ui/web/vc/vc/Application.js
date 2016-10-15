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
                },
                {
                    itemId: "import",
                    text: __("Import"),
                    glyph: NOC.glyph.level_down,
                    tooltip: __("Import VCs"),
                    hasAccess: NOC.hasPermission("import"),
                    menu: {
                        xtype: "menu",
                        plain: true,
                        items: [
                            {
                                text: __("VLANs From Switch"),
                                itemId: "vlans_from_switch",
                                glyph: NOC.glyph.level_down,
                            }
                        ],
                        listeners: {
                            click: {
                                scope: me,
                                fn: me.onImportVLANSFromSwitch
                            }
                        }
                    }
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
                },
                {
                    itemId: "add_interfaces",
                    text: __("Add Interfaces"),
                    glyph: NOC.glyph.plus_circle,
                    tooltip: __("Add interfaces to VC"),
                    hasAccess: NOC.hasPermission("set_untagged"),
                    scope: me,
                    handler: me.onAddVCInterfaces
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
        Ext.create("NOC.vc.vc.AddFirstFreeForm", {app: me});
    },
    //
    onImportVLANSFromSwitch: function() {
        Ext.create("NOC.vc.vc.MOSelectForm", {app: this});
    },
    //
    runImportFromSwitch: function(vc_domain, managed_object, vc_filter) {
        var me = this;

        me.vc_domain = vc_domain;
        me.vc_filter = vc_filter;
        // Get VC filter expression
        Ext.Ajax.request({
            url: "/vc/vcfilter/" + me.vc_filter + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                // Run MRT
                var me = this,
                    r = Ext.decode(response.responseText);
                me.vc_filter_expression = r.expression;
                NOC.mrt({
                    url: "/vc/vc/mrt/get_vlans/",
                    selector: managed_object,
                    loadMask: me,
                    scope: me,
                    success: me.processImportFromSwitch,
                    failure: function() {
                        NOC.error(__("Failed to import VLANs"))
                    }
                });
            },
            failure: function() {
                NOC.error(__("Failed to get VC Filter"));
            }
        });
    },
    //
    processImportFromSwitch: function(result) {
        var me = this,
            r = result[0];
        if(!Ext.isDefined(r)) {
            NOC.error("Failed to import VLANs.<br/>No result returned");
            return;
        }
        if(r.status) {
            // VLANS Fetched
            // r.code
            var w = Ext.create("NOC.vc.vc.VCImportForm", {
                app: me,
                vc_domain: me.vc_domain,
                vc_filter: me.vc_filter,
                vc_filter_expression: me.vc_filter_expression
            });
            w.loadVLANsFromSwitch(r.result);
        } else {
            // Failed to fetch
            NOC.error("Failed to import VLANs from {0}:<br>{1}",
                      r.object_name, r.result.text);
        }
    },
    // Called when import complete
    onImportSuccess: function(result) {
        var me = this;
        me.reloadStore();
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
    onAddVCInterfaces: function() {
        var me = this,
            vc = me.currentRecord.data;
        Ext.create("NOC.vc.vc.AddInterfacesForm", {
            app: me,
            vc: vc
        });
    },
    //
    onInterfacesCellClick: function(record) {
        var me = this;
        me.showVCInterfaces(record);
    }
});
