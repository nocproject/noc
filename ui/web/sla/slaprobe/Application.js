//---------------------------------------------------------------------
// sla.slaprobe application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprobe.Application");

Ext.define("NOC.sla.slaprobe.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sla.slaprobe.Model",
        "NOC.sa.managedobject.LookupField",
        "NOC.sla.slaprofile.LookupField"
    ],
    model: "NOC.sla.slaprobe.Model",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Managed Object"),
                    dataIndex: "managed_object",
                    width: 200,
                    renderer: NOC.render.Lookup("managed_object")
                },
                {
                    text: __("Probe"),
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("Targets"),
                    dataIndex: "targets",
                    width: 200
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "managed_object",
                    xtype: "sa.managedobject.LookupField",
                    fieldLabel: __("Managed Object"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "profile",
                    xtype: "sla.slaprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "tests",
                    xtype: "gridfield",
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
                            text: __("Target"),
                            dataIndex: "target",
                            flex: 1,
                            editor: "textfield"
                        },
                        {
                            text: __("HW. Timestamp"),
                            dataIndex: "hw_timestamp",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
