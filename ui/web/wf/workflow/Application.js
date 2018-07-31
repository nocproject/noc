//---------------------------------------------------------------------
// wf.workflow application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.Application");

Ext.define("NOC.wf.workflow.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.wf.workflow.Model",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.wf.workflow.Model",
    search: true,

    initComponent: function() {
        var me = this;
        me.WF_EDITOR = me.registerItem("NOC.wf.workflow.WFEditor");
        me.editorButton = Ext.create("Ext.button.Button", {
            text: __("Editor"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onEditor
        });
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    flex: 1
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                }
            ],

            formToolbar: [
                me.editorButton
            ]
        });
        me.callParent();
    },
    onEditor: function() {
        var me = this;
        me.previewItem(me.WF_EDITOR, me.currentRecord);
    },
    onClone: function() {
        var me = this;
        if(me.currentRecord) {
            Ext.Ajax.request({
                url: "/wf/workflow/" + me.currentRecord.get("id") + "/clone/",
                method: "POST",
                scope: me,
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    me.restoreHistory([data.id]);
                    NOC.info(__("Cloned"));
                },
                failure: function(response) {
                    NOC.error(__("Failed to clone"))
                }
            });
        }
    }
});
