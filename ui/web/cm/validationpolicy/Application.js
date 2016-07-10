//---------------------------------------------------------------------
// cm.validationpolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicy.Application");

Ext.define("NOC.cm.validationpolicy.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.cm.validationpolicy.Model",
        "NOC.cm.validationrule.LookupField"
    ],
    model: "NOC.cm.validationpolicy.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: "Active"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "rules",
                    xtype: "gridfield",
                    fieldLabel: "Rules",
                    columns: [
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: "Validation Rule",
                            dataIndex: "rule",
                            flex: 1,
                            editor: "cm.validationrule.LookupField",
                            renderer: NOC.render.Lookup("rule")
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
