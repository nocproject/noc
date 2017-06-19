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
        "NOC.project.project.LookupField",
        "NOC.phone.phonenumber.LookupField",
        "NOC.phone.phonelinktype.LookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.sa.terminationgroup.LookupField"
    ],
    model: "NOC.phone.phonenumber.Model",
    rowClassField: "row_class",
    search: true,

    statusStore: [
        ["N", "New"],
        ["F", "Free"],
        ["A", "Allocated"],
        ["R", "Reserved"],
        ["O", "Out-of-order"],
        ["C", "Cooldown"]
    ],

    protocolStore: [
        ["SIP", "SIP"],
        ["H323", "H.323"],
        ["SS7", "SS7"],
        ["MGCP", "MGCP"],
        ["H247", "H.247"],
        ["ISDN", "ISDN"],
        ["Skinny", "Skinny"]
    ],

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
                },
                {
                    text: __("Administrative Domain"),
                    dataIndex: "administrative_domain",
                    width: 100,
                    renderer: NOC.render.Lookup("administrative_domain")
                },
                {
                    text: __("Termination Group"),
                    dataIndex: "termination_group",
                    width: 100,
                    renderer: NOC.render.Lookup("termination_group")
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
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
                    store: me.statusStore,
                    uiStyle: "medium"
                },
                {
                    name: "protocol",
                    xtype: "combobox",
                    fieldLabel: __("Protocol"),
                    allowBlank: false,
                    store: me.protocolStore,
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
                },
                {
                    name: "administrative_domain",
                    xtype: "sa.administrativedomain.LookupField",
                    fieldLabel: __("Adm. Domain"),
                    allowBlank: true
                },
                {
                    name: "termination_group",
                    xtype: "sa.terminationgroup.LookupField",
                    fieldLabel: __("Termination Group"),
                    allowBlank: true
                },
                {
                    name: "linked_numbers",
                    xtype: "gridfield",
                    fieldLabel: __("Linked Numbers"),
                    columns: [
                        {
                            text: __("Type"),
                            dataIndex: "type",
                            editor: "phone.phonelinktype.LookupField",
                            renderer: NOC.render.Lookup("type"),
                            width: 150
                        },
                        {
                            text: __("Number"),
                            dataIndex: "number",
                            editor: "phone.phonenumber.LookupField",
                            renderer: NOC.render.Lookup("number"),
                            width: 150
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                }
            ],

            formToolbar: [
                me.cardButton
            ],

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
                },
                {
                    title: __("By Status"),
                    name: "status",
                    ftype: "choices",
                    store: me.statusStore
                },
                {
                    title: __("By Protocol"),
                    name: "protocol",
                    ftype: "choices",
                    store: me.protocolStore
                }
            ]
        });
        me.callParent();
    },

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
