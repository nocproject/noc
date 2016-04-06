//---------------------------------------------------------------------
// maintainance.maintainance application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintainance.maintainance.Application");

Ext.define("NOC.maintainance.maintainance.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.maintainance.maintainance.Model",
        "NOC.maintainance.maintainancetype.LookupField",
        "NOC.sa.managedobject.LookupField"
    ],
    model: "NOC.maintainance.maintainance.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Type",
                    dataIndex: "type",
                    width: 150,
                    renderer: NOC.render.Lookup("type")
                },
                {
                    text: "Start",
                    dataIndex: "start",
                    width: 100
                },
                {
                    text: "Stop",
                    dataIndex: "stop",
                    width: 100
                },
                {
                    text: "Completed",
                    dataIndex: "is_completed",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "type",
                    xtype: "maintainance.maintainancetype.LookupField",
                    fieldLabel: "Type",
                    allowBlank: false
                },
                {
                    name: "start",
                    xtype: "textfield",
                    fieldLabel: "Start",
                    allowBlank: false
                },
                {
                    name: "stop",
                    xtype: "textfield",
                    fieldLabel: "Stop",
                    allowBlank: false
                },
                {
                    name: "is_completed",
                    xtype: "checkbox",
                    boxLabel: "Completed"
                },
                {
                    name: "contacts",
                    xtype: "textarea",
                    fieldLabel: "Contacts",
                    allowBlank: false
                },
                {
                    name: "suppress_alarms",
                    xtype: "checkbox",
                    boxLabel: "Suppress alarms"
                },
                {
                    name: "direct_objects",
                    xtype: "gridfield",
                    fieldLabel: "Objects",
                    columns: [
                        {
                            text: "Object",
                            dataIndex: "object",
                            editor: "sa.managedobject.LookupField",
                            flex: 1,
                            renderer: NOC.render.Lookup("object")
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
