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
            ]
        });
        console.log(me.getRegisteredItems());
        me.getRegisteredItems()[me.WF_EDITOR].on("scriptsLoaded", function() {
            var me = this;
            if(me.openPreview){
                me.openDiagram(me.currentRecord);
            }
        }, me);
        me.callParent();
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
    },
    //
    newRecord: function() {
        var me = this;
        me.openDiagram(null);
    },
    // Show Form
    onEditRecord: function(record) {
        var me = this;
        // Check permissions
        if(!me.hasPermission("read") && !me.hasPermission("update"))
            return;
        me.currentRecord = record;
        if(me.getRegisteredItems()[me.WF_EDITOR].getScriptsLoaded()) {
            me.openDiagram(me.currentRecord);
        } else {
            me.openPreview = true;
        }
    },
    //
    openDiagram: function(record) {
        var me = this;
        me.previewItem(me.WF_EDITOR, record);
        if(record) {
            me.setHistoryHash(record.get("id"));
        }
    }
});
