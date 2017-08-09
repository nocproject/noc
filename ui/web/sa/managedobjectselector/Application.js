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
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.sa.managedobjectselector.M2MField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.main.prefixtable.LookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.vc.vcdomain.LookupField",
        "NOC.sa.terminationgroup.LookupField",
        "NOC.sa.terminationgroup.LookupField",
        "NOC.main.ref.profile.LookupField",
        "NOC.main.pool.LookupField"
    ],
    model: "NOC.sa.managedobjectselector.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.ITEM_OBJECTS = me.registerItem(
            "NOC.sa.managedobjectselector.ObjectsPanel"
        );
        me.objectsButton = Ext.create("Ext.button.Button", {
            text: __("Matched Objects"),
            glyph: NOC.glyph.list,
            scope: me,
            handler: me.onObjects
        });
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Enabled"),
                    dataIndex: "is_enabled",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Expression"),
                    dataIndex: "expression",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large",
                    labelWidth: 170
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    labelWidth: 170
                },
                {
                    name: "is_enabled",
                    xtype: "checkboxfield",
                    boxLabel: __("Is Enabled"),
                    allowBlank: false,
                    labelWidth: 170
                },
                {
                    xtype: "fieldset",
                    title: __("Filter by Main Attributes"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "filter_id",
                            xtype: "numberfield",
                            fieldLabel: __("ID"),
                            allowBlank: true,
                            hideTrigger: true,
                            uiStyle: "small",
                            labelWidth: 170
                        },
                        {
                            name: "filter_name",
                            xtype: "textfield",
                            fieldLabel: __("Name (REGEXP)"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_description",
                            xtype: "textfield",
                            fieldLabel: __("Filter by Description (REGEXP)"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_managed",
                            xtype: "combobox",
                            fieldLabel: __("Is Managed"),
                            store: [
                                [null, "-"],
                                [true, "Yes"],
                                [false, "No"]
                            ],
                            allowBlank: true,
                            uiStyle: "small",
                            labelWidth: 170
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Filter by Object Attributes"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "filter_profile",
                            xtype: "main.ref.profile.LookupField",
                            fieldLabel: __("Profile"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_object_profile",
                            xtype: "sa.managedobjectprofile.LookupField",
                            fieldLabel: __("Object Profile"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_administrative_domain",
                            xtype: "sa.administrativedomain.LookupField",
                            fieldLabel: __("Administrative Domain"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_pool",
                            xtype: "main.pool.LookupField",
                            fieldLabel: __("Pool"),
                            allowBlank: true,
                            labelWidth: 170
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Filter by Network Attributes"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "filter_termination_group",
                            xtype: "sa.terminationgroup.LookupField",
                            fieldLabel: __("Termination group"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_service_terminator",
                            xtype: "sa.terminationgroup.LookupField",
                            fieldLabel: __("Service terminator"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_vrf",
                            xtype: "ip.vrf.LookupField",
                            fieldLabel: __("VRF"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_vc_domain",
                            xtype: "vc.vcdomain.LookupField",
                            fieldLabel: __("VC Domain"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_address",
                            xtype: "textfield",
                            fieldLabel: __("Address (REGEXP)"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_prefix",
                            xtype: "main.prefixtable.LookupField",
                            fieldLabel: __("Prefix Table"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Filter by Other"),
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "filter_user",
                            xtype: "textfield",
                            fieldLabel: __("User (REGEXP)"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_remote_path",
                            xtype: "textfield",
                            fieldLabel: __("Path (REGEXP)"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        },
                        {
                            name: "filter_tags",
                            xtype: "textfield",
                            fieldLabel: __("Filter By Tags"),
                            allowBlank: true,
                            uiStyle: "large",
                            labelWidth: 170
                        }
                    ]
                },
                {
                    name: "source_combine_method",
                    xtype: "combobox",
                    fieldLabel: __("Source Combine Method"),
                    store: [
                        ["O", "OR"],
                        ["A", "AND"]
                    ],
                    allowBlank: false,
                    uiStyle: "small",
                    labelWidth: 170
                },
                {
                    xtype: "sa.managedobjectselector.M2MField",
                    name: "sources",
                    height: 220,
                    width: 600,
                    fieldLabel: __("Sources"),
                    buttons: ["add", "remove"],
                    allowBlank: true,
                    uiStyle: "large",
                    labelWidth: 170
                }
            ],
            inlines: [
                {
                    title: __("Filter by attributes"),
                    model: "NOC.sa.managedobjectselector.AttributesModel",
                    columns: [
                        {
                            text: __("Key (RE)"),
                            dataIndex: "key_re",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Value (RE)"),
                            dataIndex: "value_re",
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                }
            ],
            formToolbar: [
                me.objectsButton
            ]
        });
        me.callParent();
    },
    //
    onObjects: function() {
        var me = this;
        me.previewItem(me.ITEM_OBJECTS, me.currentRecord);
    }
});
