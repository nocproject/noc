//---------------------------------------------------------------------
// sa.resourcetemplate application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.resourcetemplate.Application");

Ext.define("NOC.sa.resourcetemplate.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.sa.resourcetemplate.Model",
        "NOC.sa.profile.LookupField",
        "NOC.inv.capability.LookupField",
        "NOC.inv.resourcegroup.LookupField",
        "NOC.core.label.LabelField",
        "NOC.main.ref.modelid.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.sa.resourcetemplate.Model",
    search: true,
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/sa/resourcetemplate/{id}/json/'),
            previewName: new Ext.XTemplate('Resource Template: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Blt"),
                    // tooltip: "Built-in", - broken in ExtJS 5.1
                    dataIndex: "is_builtin",
                    width: 40,
                    renderer: NOC.render.Bool,
                    align: "center"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    text: __("Resource"),
                    dataIndex: "resource_model",
                    width: 70
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 70
                },
                {
                    text: __("Allow Manual"),
                    dataIndex: "allow_manual",
                    width: 50,
                    renderer: NOC.render.Bool,
                    align: "center"
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description")
                },
                {
                    name: "params",
                    xtype: "gridfield",
                    fieldLabel: __("Fields"),
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            width: 100,
                            sortable: false,
                            editor: {
                                xtype: "textfield",
                            }
                        },
                        {
                            text: __("Ignore"),
                            dataIndex: "ignore",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50
                        },
                        {
                            text: __("Required"),
                            dataIndex: "required",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50
                        },
                        {
                            text: __("Param"),
                            dataIndex: "param",
                            width: 100,
                            sortable: false,
                            editor: {
                                xtype: "textfield",
                            }
                        },
                        {
                            text: __("Default expression"),
                            dataIndex: "default_expression",
                            width: 200,
                            sortable: false,
                            editor: {
                                xtype: "textfield",
                            }
                        },
                        {
                          text: __("Capability"),
                          dataIndex: "set_capability",
                          renderer: NOC.render.Lookup("set_capability"),
                          width: 250,
                          editor: "inv.capability.LookupField",
                        }
                    ]
                },
                {
                    name: "groups",
                    xtype: "gridfield",
                    fieldLabel: __("Fields"),
                    columns: [
                        {
                          dataIndex: "group",
                          text: __("Resource Group"),
                          width: 350,
                          renderer: NOC.render.Lookup("group"),
                          editor: {
                            xtype: "inv.resourcegroup.LookupField",
                          },
                        },
                        {
                            text: __("Action"),
                            dataIndex: "action",
                            width: 150,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["set", __("Set")],
                                    ["allow", __("Allow")],
                                    ["deny", __("Deny")],
                                ],
                                queryMode: "local",
                            },
                            renderer: NOC.render.Lookup("action")
                        },
                        {
                            text: __("Client"),
                            dataIndex: "as_client",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50
                        },
                        {
                            text: __("Service"),
                            dataIndex: "as_service",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50
                        }
                    ]
                },
                {
                    name: "params_form",
                    xtype: "gridfield",
                    fieldLabel: __("Params Form"),
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            width: 100,
                            sortable: false,
                            editor: {
                                xtype: "textfield",
                            }
                        },
                        {
                            text: __("Hint"),
                            dataIndex: "hint",
                            width: 100,
                            sortable: false,
                            editor: {
                                xtype: "textfield",
                            }
                        },
                        {
                            text: __("Is Hide"),
                            dataIndex: "hide",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __('ModelID'),
                            dataIndex: 'model_id',
                            renderer: NOC.render.Lookup('model_id'),
                            editor: 'main.ref.modelid.LookupField',
                            width: 150
                        },
                        {
                            text: __("Validation"),
                            dataIndex: "validation_method",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["regex", "Regex"],
                                    ["eq", "Equal"],
                                    ["range", "Range"],
                                    ["choices", "Choices"]
                                ]
                            }
                        },
                        {
                            text: __("Validataion Expr."),
                            dataIndex: "validation_expression",
                            width: 100,
                            sortable: false,
                            editor: {
                                xtype: "textfield",
                            }
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ],
            filters: [
            ]
        });
        me.callParent();
    },

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
