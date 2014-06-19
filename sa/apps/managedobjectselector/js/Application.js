//---------------------------------------------------------------------
// sa.managedobjectselector application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectselector.Application");

Ext.define("NOC.sa.managedobjectselector.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.managedobjectselector.Model",
        "NOC.sa.managedobjectselector.AttributesModel",
        "NOC.sa.managedobjectselector.M2MField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.main.prefixtable.LookupField",
        "NOC.main.shard.LookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.sa.activator.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.vc.vcdomain.LookupField",
        "NOC.sa.terminationgroup.LookupField",
        "NOC.sa.terminationgroup.LookupField"
    ],
    model: "NOC.sa.managedobjectselector.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Enabled",
                    dataIndex: "is_enabled",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Expression",
                    dataIndex: "expression",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "is_enabled",
                    xtype: "checkboxfield",
                    boxLabel: "Is Enabled",
                    allowBlank: false
                },
                {
                    name: "filter_id",
                    xtype: "numberfield",
                    fieldLabel: "Filter by ID",
                    allowBlank: true
                },
                {
                    name: "filter_name",
                    xtype: "textfield",
                    fieldLabel: "Filter by Name (REGEXP)",
                    allowBlank: true
                },
                {
                    name: "filter_managed",
                    xtype: "combobox",
                    fieldLabel: "Filter by Is Managed",
                    allowBlank: true,
                    store: [
                        [null, "-"],
                        [true, "Is managed"],
                        [false, "Not Managed"]
                    ]
                },
                {
                    name: "filter_profile",
                    xtype: "textfield",
                    fieldLabel: "Filter by Profile",
                    allowBlank: true
                },
                {
                    name: "filter_object_profile",
                    xtype: "sa.managedobjectprofile.LookupField",
                    fieldLabel: "Filter by Object Profile",
                    allowBlank: true
                },
                {
                    name: "filter_address",
                    xtype: "textfield",
                    fieldLabel: "Filter by Address (REGEXP)",
                    allowBlank: true
                },
                {
                    name: "filter_prefix",
                    xtype: "main.prefixtable.LookupField",
                    fieldLabel: "Filter by Prefix Table",
                    allowBlank: true
                },
                {
                    name: "filter_shard",
                    xtype: "main.shard.LookupField",
                    fieldLabel: "Filter by Shard",
                    allowBlank: true
                },
                {
                    name: "filter_administrative_domain",
                    xtype: "sa.administrativedomain.LookupField",
                    fieldLabel: "Filter by Administrative Domain",
                    allowBlank: true
                },
                {
                    name: "filter_activator",
                    xtype: "sa.activator.LookupField",
                    fieldLabel: "Filter by Activator",
                    allowBlank: true
                },
                {
                    name: "filter_vrf",
                    xtype: "ip.vrf.LookupField",
                    fieldLabel: "Filter by VRF",
                    allowBlank: true
                },
                {
                    name: "filter_vc_domain",
                    xtype: "vc.vcdomain.LookupField",
                    fieldLabel: "Filter by VC Domain",
                    allowBlank: true
                },
                {
                    name: "filter_termination_group",
                    xtype: "sa.terminationgroup.LookupField",
                    fieldLabel: "Filter by termination group",
                    allowBlank: true
                },
                {
                    name: "filter_service_terminator",
                    xtype: "sa.terminationgroup.LookupField",
                    fieldLabel: "Filter by service terminator",
                    allowBlank: true
                },
                {
                    name: "filter_user",
                    xtype: "textfield",
                    fieldLabel: "Filter by User (REGEXP)",
                    allowBlank: true
                },
                {
                    name: "filter_remote_path",
                    xtype: "textfield",
                    fieldLabel: "Filter by Remote Path (REGEXP)",
                    allowBlank: true
                },
                {
                    name: "filter_description",
                    xtype: "textfield",
                    fieldLabel: "Filter by Description (REGEXP)",
                    allowBlank: true
                },
                {
                    name: "filter_repo_path",
                    xtype: "textfield",
                    fieldLabel: "Filter by Repo Path (REGEXP)",
                    allowBlank: true
                },
                {
                    name: "filter_tags",
                    xtype: "textfield",
                    fieldLabel: "Filter By Tags",
                    allowBlank: true
                },
                {
                    name: "source_combine_method",
                    xtype: "combobox",
                    fieldLabel: "Source Combine Method",
                    allowBlank: false,
                    store: [
                        ["O", "OR"],
                        ["A", "AND"]
                    ]
                },
                {
                    xtype: "sa.managedobjectselector.M2MField",
                    name: "sources",
                    height: 220,
                    width: 600,
                    fieldLabel: "Sources",
                    buttons: ["add", "remove"],
                    allowBlank: true
                }
            ],
            inlines: [
                {
                    title: "Filter by attributes",
                    model: "NOC.sa.managedobjectselector.AttributesModel",
                    columns: [
                        {
                            text: "Key (RE)",
                            dataIndex: "key_re",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Value (RE)",
                            dataIndex: "value_re",
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
