//---------------------------------------------------------------------
// support.crashinfo application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.crashinfo.Application");

Ext.define("NOC.support.crashinfo.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.support.crashinfo.Model"
    ],
    model: "NOC.support.crashinfo.Model",

    initComponent: function() {
        var me = this;
        me.tbField = null;
        Ext.apply(me, {
            columns: [
                {
                    text: "UUID",
                    dataIndex: "uuid",
                    width: 220
                },
                {
                    text: "Timestamp",
                    dataIndex: "timestamp",
                    width: 170
                },
                {
                    text: "Status",
                    dataIndex: "status",
                    width: 50,
                    renderer: NOC.render.Choices({
                        N: "New",
                        r: "To report",
                        R: "Reported",
                        X: "Rejected",
                        f: "Fix ready",
                        F: "Fixed"
                    })
                },
                {
                    text: "Priority",
                    dataIndex: "priority",
                    width: 70,
                    renderer: NOC.render.Choices({
                        I: "Info",
                        L: "Low",
                        M: "Medium",
                        H: "High",
                        C: "Critical"
                    })
                },
                {
                    text: "Branch",
                    dataIndex: "branch",
                    width: 120  // @todo: bitbucket branch
                },
                {
                    text: "Tip",
                    dataIndex: "tip",
                    width: 150  // @todo: bitbucket renderer
                },
                {
                    text: "Process",
                    dataIndex: "process",
                    flex: 1
                }
            ],

            fields: [
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    defaults: {
                        padding: 4
                    },
                    border: 0,
                    items: [
                        {
                            xtype: "displayfield",
                            fieldLabel: "UUID",
                            name: "uuid"
                        },
                        {
                            xtype: "displayfield",
                            fieldLabel: "Timestamp",
                            name: "timestamp"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    defaults: {
                        padding: 4
                    },
                    border: 0,
                    items: [
                        {
                            xtype: "displayfield",
                            fieldLabel: "Status",
                            name: "status"
                        },
                        {
                            xtype: "displayfield",
                            fieldLabel: "Priority",
                            name: "priority"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    defaults: {
                        padding: 4
                    },
                    border: 0,
                    items: [
                        {
                            xtype: "displayfield",
                            fieldLabel: "Branch",
                            name: "branch"
                        },
                        {
                            xtype: "displayfield",
                            fieldLabel: "Changeset",
                            name: "tip"
                        }
                    ]
                },
                {
                    xtype: "textarea",
                    fieldLabel: "Comment",
                    name: "comment"
                },
                {
                    xtype: "container",
                    itemId: "tb"
                }
            ]
        });
        me.callParent();
    },
    //
    showForm: function() {
        var me = this;
        me.callParent();
        Ext.Ajax.request({
            method: "GET",
            url: "/support/crashinfo/" + me.currentRecord.get("uuid") + "/traceback/",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.setTraceback(data);
            }
        });
    },
    //
    setTraceback: function(tb) {
        var me = this;
        if(!me.tbField) {
            me.tbField = me.formPanel.items.first().getComponent("tb");
        }
        me.tbField.setHtml("<pre style='border: 1px solid gray; padding: 4px; border-radius: 4px'>" + tb + "</pre>");
    }
});
