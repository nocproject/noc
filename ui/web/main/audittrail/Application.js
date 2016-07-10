//---------------------------------------------------------------------
// main.audittrail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.audittrail.Application");

Ext.define("NOC.main.audittrail.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.audittrail.Model",
        "NOC.main.ref.model.LookupField",
        "NOC.main.user.LookupField"
    ],
    model: "NOC.main.audittrail.Model",
    search: true,
    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: "Timestamp",
                    dataIndex: "timestamp",
                    width: 160
                },
                {
                    text: "User",
                    dataIndex: "user",
                    width: 100
                },
                {
                    text: "Model",
                    dataIndex: "model_id",
                    width: 150
                },
                {
                    text: "Operation",
                    dataIndex: "op",
                    flex: 1,
                    renderer: NOC.render.Choices({
                        "C": "Create",
                        "M": "Modify",
                        "D": "Delete"
                    })
                }
            ],
            fields: [
                {
                    name: "timestamp",
                    xtype: "displayfield",
                    fieldLabel: "Timestamp"
                },
                {
                    name: "user",
                    xtype: "displayfield",
                    fieldLabel: "User"
                },
                {
                    name: "model_id",
                    xtype: "displayfield",
                    fieldLabel: "Model"
                },
                {
                    name: "op",
                    xtype: "displayfield",
                    fieldLabel: "Operation"
                },
                {
                    name: "changes",
                    xtype: "displayfield",
                    fieldLabel: "Changes",
                    renderer: NOC.render.Table({
                        columns: [
                            {
                                text: "Field",
                                dataIndex: "field"
                            },
                            {
                                text: "Old",
                                dataIndex: "old"
                            },
                            {
                                text: "New",
                                dataIndex: "new"
                            }
                        ]
                    })
                }
            ]
        });
        me.callParent();
        me.saveButton.hide();
    }
});
