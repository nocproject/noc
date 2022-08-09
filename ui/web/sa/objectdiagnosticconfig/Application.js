//---------------------------------------------------------------------
// sa.objectdiagnosticconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectdiagnosticconfig.Application");

Ext.define("NOC.sa.objectdiagnosticconfig.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.core.ListFormField",
        "NOC.core.tagfield.Tagfield",
        "Ext.ux.form.GridField",
        "Ext.ux.form.StringsField",
        "NOC.main.ref.check.LookupField",
        "NOC.sa.diagnosticconfig.LookupField",
        "NOC.fm.alarmclass.LookupField"
    ],
    model: "NOC.sa.objectdiagnosticconfig.Model",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 200
        },
        {
            text: __('Builtin'),
            dataIndex: 'is_builtin',
            renderer: NOC.render.Bool,
            width: 30
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 200
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: 'uuid',
            xtype: 'displayfield',
            style: 'padding-left: 10px',
            fieldLabel: __('UUID')
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "is_active",
            xtype: "checkbox",
            boxLabel: __("Active"),
            allowBlank: true
        },
        {
            xtype: "fieldset",
            title: __("Display Settings"),
            items: [
                {
                    name: "display_order",
                    xtype: "numberfield",
                    fieldLabel: __("Display Order"),
                    uiStyle: "small",
                    value: 800,
                    minValue: 0,
                    allowBlank: true
                },
                {
                    name: "show_in_display",
                    xtype: "checkbox",
                    boxLabel: __("Show in form"),
                    allowBlank: true
                }
           ]
        },
        {
            xtype: "fieldset",
            title: __("Alarm"),
            items: [
                {
                    name: "alarm_class",
                    xtype: "fm.alarmclass.LookupField",
                    fieldLabel: __("Alarm Class"),
                    uiStyle: 'large',
                    allowBlank: true
                },
                {
                    name: "alarm_labels",
                    xtype: "labelfield",
                    fieldLabel: __("Alarm Labels"),
                    allowBlank: true,
                    isTree: false,
                    filterProtected: false,
                    pickerPosition: "down",
                    uiStyle: "extra",
                    query: {
                        "enable_alarm": true
                    }
                }
            ]
        },
        {
            name: "state_policy",
            xtype: "combobox",
            fieldLabel: __("State Policy"),
            store: [
                ["ALL", __("ALL")],
                ["ANY", __("ANY")]
            ],
            allowBlank: true,
            value: "ANY",
            uiStyle: "large"
        },
        {
            name: "checks",
            fieldLabel: __("Checks"),
            xtype: "gridfield",
            allowBlank: true,
            columns: [
                {
                    text: __("Check"),
                    dataIndex: "check",
                    width: 200,
                    editor: {
                        xtype: "main.ref.check.LookupField"
                    },
                    allowBlank: false,
                    renderer: NOC.render.Lookup("check")
                },
                {
                    text: __("Argument"),
                    dataIndex: "arg0",
                    editor: "textfield",
                    width: 150
                },
            ]
        },
        {
            xtype: "core.tagfield",
            url: "/sa/objectdiagnosticconfig/lookup/",
            fieldLabel: __("Diagnostics"),
            name: "diagnostics",
        },
        {
            name: "runs",
            fieldLabel: __("Run Config"),
            xtype: "gridfield",
            allowBlank: true,
            columns: [
                {
                    text: __("Box"),
                    dataIndex: "enable_box",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Periodic"),
                    dataIndex: "enable_periodic",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Save History"),
                    dataIndex: "save_history",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Run Policy"),
                    dataIndex: "run_policy",
                    width: 100,
                    editor: {
                        xtype: "combobox",
                        store: [
                            ["A", __("Always")],
                            ["F", __("Unknown or Failed")],
                            ["M", __("Manual")]
                        ]
                    },
                    renderer: NOC.render.Choices({
                        "A": __("Persistent"),
                        "F": __("Unknown or Failed"),
                        "M": __("Manual")
                    })
                },
                {
                    text: __("Run Order"),
                    dataIndex: "run_order",
                    width: 100,
                    editor: {
                        xtype: "combobox",
                        store: [
                            ["A", __("After")],
                            ["B", __("Before")]
                        ]
                    },
                    renderer: NOC.render.Choices({
                        "A": __("After"),
                        "B": __("Before")
                    })
                }
            ]
        },
    ]
});
