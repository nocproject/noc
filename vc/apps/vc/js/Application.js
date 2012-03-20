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
        "NOC.core.TagsField",
        "NOC.vc.vcdomain.LookupField"
    ],
    model: "NOC.vc.vc.Model",
    search: true,

    columns: [
        {
            text: "VC Domain",
            dataIndex: "vc_domain__label"
        },
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Label",
            dataIndex: "label",
            width: 50
        },
        {
            text: "L1",
            dataIndex: "l1",
            width: 25,
            hidden: true
        },
        {
            text: "L2",
            dataIndex: "l2",
            width: 25,
            hidden: true
        },
        {
            text: "Int.",
            dataIndex: "interfaces_count",
            width: 50
        },
        {
            text: "Prefixes",
            dataIndex: "prefixes",
            width: 100
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        },
        {
            text: "Tags",
            dataIndex: "tags",
            renderer: noc_renderTags
        },
        {
            xtype: "actioncolumn",
            width: 50,
            items: [
                {
                    icon: "/static/img/fam/silk/information.png",
                    tooltip: "Show Interfaces",
                    handler: function(grid, rowIndex, colIndex) {
                        var me = grid.up("panel").up("panel"),
                            vc = grid.getStore().getAt(rowIndex);
                        me.showInterfaces(vc.data);
                    }
                }
            ]
        }
    ],
    fields: [
        {
            name: "vc_domain",
            xtype: "vc.vcdomain.LookupField",
            fieldLabel: "VC Domain",
            allowBlank: false
        },
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false,
            regex: /^[a-zA-Z0-9_\-]+$/
        },
        {
            name: "l1",
            xtype: "numberfield",
            fieldLabel: "L1",
            allowBlank: false
        },
        { // @todo: Auto-hide when VC domain does not support l2
            name: "l2",
            xtype: "numberfield",
            fieldLabel: "L2",
            allowBlank: true
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By VC Domain",
            name: "vc_domain",
            ftype: "lookup",
            lookup: "vc.vcdomain"
        },
        {
            title: "By VC Filter",
            name: "l1",
            ftype: "vcfilter"
        },
        {
            title: "By Tags",
            name: "tags",
            ftype: "tag"
        }
    ],
    toolbar: [
        {
            itemId: "create_first",
            text: "Add First Free",
            iconCls: "icon_application_form_add",
            tooltip: "Add first free VC",
            handler: function() {
                var app = this.up("panel").up("panel");
                app.first_new_record();
            }
        },
        {
            itemId: "import",
            text: "Import",
            iconCls: "icon_door_in",
            tooltip: "Import VCs",
            menu: {
                xtype: "menu",
                plain: true,
                items: [
                    {
                        text: "VLANs From Switch",
                        itemId: "vlans_from_switch",
                        iconCls: "icon_arrow_right"
                    }
                ]
            }
        }
    ],
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        // Set up import menu
        var importMenu = me.grid_toolbar.getComponent("import").menu,
            VLANSFromSwitchItem = importMenu.getComponent("vlans_from_switch");

        VLANSFromSwitchItem.mon(VLANSFromSwitchItem, "click",
                                me.onImportVLANSFromSwitch, me);
    },
    //
    first_new_record: function() {
        var me = this;
        Ext.create("NOC.vc.vc.AddFirstFreeForm", {
            callback: Ext.bind(me.on_first_new_record, me),
            renderTo: me.el
        });
    },
    //
    on_first_new_record: function(vc_domain, vc) {
        var me = this;
        console.log(vc_domain, vc);
        me.new_record({vc_domain: vc_domain, l1: vc});
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
                    scope: me,
                    success: me.processImportFromSwitch,
                    failure: function() {
                        NOC.error("Failed to import VLANs")
                    }
                });
            },
            failure: function() {
                NOC.error("Failed to get VC Filter");
            }
        });
    },
    //
    processImportFromSwitch: function(result) {
        var me = this,
            r = result[0];
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
        me.refresh_store();
    },
    // Show interfaces window
    showInterfaces: function(vc) {
        var me = this;
        Ext.Ajax.request({
            url: "/vc/vc/" + vc.id + "/interfaces/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                Ext.create("NOC.vc.vc.VCInterfaces", {
                    app: me,
                    vc: vc,
                    interfaces: r
                });
            },
            failure: function() {
                NOC.error("Failed to get interfaces");
            }
        });
    },
    // Parse additional permissions
    set_permissions: function(permissions) {
        var me = this;
        me.callParent([permissions]);
        // Set import permissions
        me.can_import = permissions.indexOf("import") >= 0;
        var i_menu = me.grid.dockedItems.items[1].getComponent("import");
        if(!me.can_import)
            i_menu.hide();
    }
});
