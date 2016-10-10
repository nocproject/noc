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
                    text: __("Timestamp"),
                    dataIndex: "timestamp",
                    width: 160
                },
                {
                    text: __("User"),
                    dataIndex: "user",
                    width: 100
                },
                {
                    text: __("Model"),
                    dataIndex: "model_id",
                    width: 150
                },
                {
                    text: __("Operation"),
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
                    fieldLabel: __("Timestamp")
                },
                {
                    name: "user",
                    xtype: "displayfield",
                    fieldLabel: __("User")
                },
                {
                    name: "model_id",
                    xtype: "displayfield",
                    fieldLabel: __("Model")
                },
                {
                    name: "op",
                    xtype: "displayfield",
                    fieldLabel: __("Operation")
                // },
                // {
                //     name: "changes",
                //     xtype: "displayfield",
                //     fieldLabel: __("Changes")
                    // renderer: NOC.render.Table({
                    //     columns: [
                    //         {
                    //             text: __("Field"),
                    //             dataIndex: "field"
                    //         },
                    //         {
                    //             text: __("Old"),
                    //             dataIndex: "old"
                    //         },
                    //         {
                    //             text: __("New"),
                    //             dataIndex: "new"
                    //         }
                    //     ]
                    // })
                }
            ]
        });
        me.callParent();
        me.saveButton.hide();
    }
});
