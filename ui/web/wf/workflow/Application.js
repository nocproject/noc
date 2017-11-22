//---------------------------------------------------------------------
// wf.workflow application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.Application");

Ext.define("NOC.wf.workflow.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.wf.workflow.Model",
        "NOC.wf.solution.LookupField",
        "NOC.wf.workflow.LanesModel",
        "NOC.wf.workflow.VariablesModel"
    ],
    model: "NOC.wf.workflow.Model",
    columns: [
        {
            text: __("Solution"),
            dataIndex: "solution",
            renderer: NOC.render.Lookup("solution"),
            width: 150
        },
        {
            text: __("Name"),
            dataIndex: "name",
            width: 100
        },
        {
            text: __("Display Name"),
            dataIndex: "display_name",
            width: 150
        },
        {
            text: __("Version"),
            dataIndex: "version",
            width: 70
        },
        {
            text: __("Act"),
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: __("Trace"),
            dataIndex: "trace",
            renderer: NOC.render.Bool,
            width: 50
        }
    ],
    fields: [
        {
            name: "solution",
            fieldLabel: __("Solution"),
            xtype: "wf.solution.LookupField",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "name",
            fieldLabel: __("Name"),
            xtype: "textfield",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "display_name",
            fieldLabel: __("Display Name"),
            xtype: "textfield",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "version",
            xtype: "numberfield",
            fieldLabel: __("Version"),
            allowBlank: false,
            defaultValue: 1
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: __("Active")
        },
        {
            name: "description",
            xtype: "textarea",
            allowBlank: true,
            fieldLabel: __("Description"),
            anchor: "100%"
        },
        {
            name: "trace",
            xtype: "checkboxfield",
            boxLabel: __("Trace")
        }
    ],
    inlines: [
        {
            title: __("Variables"),
            model: "NOC.wf.workflow.VariablesModel",
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100,
                    editor: "textfield"
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 100,
                    editor: "textfield"
                },
                {
                    text: __("Req"),
                    dataIndex: "required",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkboxfield"
                },
                {
                    text: __("Default"),
                    dataIndex: "default",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1,
                    editor: "textfield"
                }
            ]
        },
        {
            title: __("Lanes"),
            model: "NOC.wf.workflow.LanesModel",
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: __("Act"),
                    dataIndex: "is_active",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkboxfield"
                }
            ]
        }
    ],
    //
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            formToolbar: [
                {
                    itemId: "wfedit",
                    text: __("WF Editor"),
                    glyph: NOC.glyph.pencil,
                    tooltip: __("Workflow Editor"),
                    scope: me,
                    handler: me.onWFEditor
                }
            ]
        });
        me.callParent();
    },
    //
    onWFEditor: function() {
        var me = this;
        Ext.create("NOC.wf.workflow.WFEditor", {
            app: me,
            wf: me.currentRecord
        });
    }
});
