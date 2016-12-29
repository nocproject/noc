//---------------------------------------------------------------------
// phone.phonenumber application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonenumber.Application");

Ext.define("NOC.phone.phonenumber.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.phone.phonenumber.Model",
        "NOC.phone.dialplan.LookupField",
        "NOC.phone.phonenumberprofile.LookupField",
        "NOC.phone.numbercategory.LookupField",
        "NOC.phone.phonerange.LookupField",
        "NOC.project.project.LookupField"
    ],
    model: "NOC.phone.phonenumber.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        Ext.apply(me, {
            columns: [
                {
                    text: __("Dialplan"),
                    dataIndex: "dialplan",
                    width: 150,
                    renderer: NOC.render.Lookup("dialplan")
                },
                {
                    text: __("Number"),
                    dataIndex: "number",
                    width: 100
                },
                {
                    text: __("Status"),
                    dataIndex: "status",
                    width: 50
                },
                {
                    text: __("Protocol"),
                    dataIndex: "protocol",
                    width: 50
                },
                {
                    text: __("Range"),
                    dataIndex: "phone_range",
                    width: 150,
                    renderer: NOC.render.Lookup("phone_range")
                },
                {
                    text: __("Category"),
                    dataIndex: "category",
                    width: 150,
                    renderer: NOC.render.Lookup("category")
                }
            ],

            fields: [
                {
                    name: "dialplan",
                    xtype: "phone.dialplan.LookupField",
                    fieldLabel: __("Dialplan"),
                    allowBlank: false
                },
                {
                    name: "number",
                    xtype: "textfield",
                    fieldLabel: __("Number"),
                    regex: /^\d+$/,
                    regexText: __("Must contain only numbers"),
                    allowBlank: false
                },
                {
                    name: "profile",
                    xtype: "phone.phonenumberprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: true
                },
                {
                    name: "phone_range",
                    xtype: "phone.phonerange.LookupField",
                    fieldLabel: __("Range"),
                    allowBlank: true
                },
                {
                    name: "category",
                    xtype: "phone.numbercategory.LookupField",
                    fieldLabel: __("Category"),
                    allowBlank: true
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: __("Status"),
                    allowBlank: false,
                    store: [
                        ["N", "New"],
                        ["F", "Free"],
                        ["A", "Allocated"],
                        ["R", "Reserved"],
                        ["O", "Out-of-order"],
                        ["C", "Cooldown"]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "protocol",
                    xtype: "combobox",
                    fieldLabel: __("Protocol"),
                    allowBlank: false,
                    store: [
                        ["SIP", "SIP"],
                        ["H323", "H.323"],
                        ["SS7", "SS7"],
                        ["MGCP", "MGCP"],
                        ["H247", "H.247"],
                        ["ISDN", "ISDN"],
                        ["Skinny", "Skinny"]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: __("Project"),
                    allowBlank: true
                }
            ],

            formToolbar: [
                me.cardButton
            ]
        });
        me.callParent();
    },

    filters: [
        {
            title: __("By Dialplan"),
            name: "dialplan",
            ftype: "lookup",
            lookup: "phone.dialplan"
        },
        {
            title: __("By Range"),
            name: "phone_range",
            ftype: "tree",
            lookup: "phone.phonerange"
        },
        {
            title: __("By Category"),
            name: "category",
            ftype: "lookup",
            lookup: "phone.numbercategory"
        }
    ],

    //
    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/phonenumber/" + me.currentRecord.get("id") + "/"
            );
        }
    }
});
