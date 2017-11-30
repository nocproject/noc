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
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 200,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("State"),
                    dataIndex: "state",
                    width: 200,
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    width: 150,
                    render: NOC.render.Tags
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "profile",
                    xtype: "crm.subscriberprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    uiStyle: "expand"
                },
                {
                    name: "address",
                    xtype: "textfield",
                    fieldLabel: __("Address"),
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "tech_contact_person",
                    xtype: "textfield",
                    fieldLabel: __("Contact"),
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "tech_contact_phone",
                    xtype: "textfield",
                    fieldLabel: __("Phone"),
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
