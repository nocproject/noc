//---------------------------------------------------------------------
// wf.workflow application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.Application");

Ext.define("NOC.wf.workflow.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.wf.workflow.Model",
        "NOC.wf.solution.LookupField",
        "NOC.wf.workflow.LanesModel",
        "NOC.wf.workflow.VariablesModel",
        "NOC.wf.workflow.templates.NodeTooltip"
    ],
    model: "NOC.wf.workflow.Model",
    columns: [
        {
            text: "Solution",
            dataIndex: "solution",
            renderer: NOC.render.Lookup("solution"),
            width: 150
        },
        {
            text: "Name",
            dataIndex: "name",
            width: 100
        },
        {
            text: "Display Name",
            dataIndex: "display_name",
            width: 150
        },
        {
            text: "Version",
            dataIndex: "version",
            width: 70
        },
        {
            text: "Act",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Trace",
            dataIndex: "trace",
            renderer: NOC.render.Bool,
            width: 50
        }
    ],
    fields: [
        {
            name: "solution",
            fieldLabel: "Solution",
            xtype: "wf.solution.LookupField",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "name",
            fieldLabel: "Name",
            xtype: "textfield",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "display_name",
            fieldLabel: "Display Name",
            xtype: "textfield",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "version",
            xtype: "numberfield",
            fieldLabel: "Version",
            allowBlank: false,
            defaultValue: 1
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "description",
            xtype: "textarea",
            allowBlank: true,
            fieldLabel: "Description",
            anchor: "100%"
        },
        {
            name: "trace",
            xtype: "checkboxfield",
            boxLabel: "Trace"
        }
    ],
    inlines: [
        {
            title: "Variables",
            model: "NOC.wf.workflow.VariablesModel",
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 100,
                    editor: "textfield"
                },
                {
                    text: "Type",
                    dataIndex: "type",
                    width: 100,
                    editor: "textfield"
                },
                {
                    text: "Req",
                    dataIndex: "required",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkboxfield"
                },
                {
                    text: "Default",
                    dataIndex: "default",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1,
                    editor: "textfield"
                }
            ]
        },
        {
            title: "Lanes",
            model: "NOC.wf.workflow.LanesModel",
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: "Act",
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
                    text: "WF Editor",
                    glyph: NOC.glyph.pencil,
                    tooltip: "Workflow Editor",
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
