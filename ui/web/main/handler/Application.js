//---------------------------------------------------------------------
// main.handler application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.handler.Application");

Ext.define("NOC.main.handler.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.handler.Model"
    ],
    model: "NOC.main.handler.Model",
    search: true,
    helpId: "reference-handler",

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
                    text: __("Handler"),
                    dataIndex: "handler",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "meduim"
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: __("Handler"),
                    allowBlank: false,
                    vtype: "handler",
                    uiStyle: "large"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: __("Config handler"),
                    layout: "vbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "allow_config_filter",
                            xtype: "checkbox",
                            boxLabel: __("Allow Config Filter")
                        },
                        {
                            name: "allow_config_validation",
                            xtype: "checkbox",
                            boxLabel: __("Allow Config Validation")
                        },
                        {
                            name: "allow_config_diff",
                            xtype: "checkbox",
                            boxLabel: __("Allow Config Diff")
                        },
                        {
                            name: "allow_config_diff_filter",
                            xtype: "checkbox",
                            boxLabel: __("Allow Config Diff Filter")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Managed Object Profile handlers"),
                    layout: "vbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "allow_housekeeping",
                            xtype: "checkbox",
                            boxLabel: __("Allow housekeeping")
                        },
                        {
                            name: "allow_resolver",
                            xtype: "checkbox",
                            boxLabel: __("Allow Resolver")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Threshold Profiles Handlers"),
                    layout: "vbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "allow_threshold",
                            xtype: "checkbox",
                            boxLabel: __("Allow Threshold Alarm")
                        },
                        {
                            name: "allow_threshold_handler",
                            xtype: "checkbox",
                            boxLabel: __("Allow Threshold Handler")
                        },
                        {
                            name: "allow_threshold_value_handler",
                            xtype: "checkbox",
                            boxLabel: __("Allow Threshold Value Handler")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Topology handlers"),
                    layout: "vbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "allow_ifdesc",
                            xtype: "checkbox",
                            boxLabel: __("Allow IfDesc")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("DataStream handlers"),
                    layout: "vbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "allow_ds_filter",
                            xtype: "checkbox",
                            boxLabel: __("Allow DataStream filter")
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("MX handlers"),
                    layout: "vbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "allow_mx_transmutation",
                            xtype: "checkbox",
                            boxLabel: __("Allow MX Transmutation")
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
