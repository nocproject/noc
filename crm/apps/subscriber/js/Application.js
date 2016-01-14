//---------------------------------------------------------------------
// crm.subscriber application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriber.Application");

Ext.define("NOC.crm.subscriber.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.crm.subscriber.Model",
        "NOC.crm.subscriberprofile.LookupField"
    ],
    model: "NOC.crm.subscriber.Model",
    search: true,
    rowClassField: "row_class",

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
                    text: "Profile",
                    dataIndex: "profile",
                    width: 200,
                    renderer: NOC.render.Lookup("profile"),
                    flex: 1
                },
                {
                    text: "Tags",
                    dataIndex: "tags",
                    width: 150,
                    render: NOC.render.Tags
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "profile",
                    xtype: "crm.subscriberprofile.LookupField",
                    fieldLabel: "Profile",
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true,
                    uiStyle: "expand"
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: "Tags",
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
