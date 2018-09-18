//---------------------------------------------------------------------
// phone.phonenumber application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
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
        "NOC.sa.administrativedomain.LookupField",
        "NOC.inv.resourcegroup.LookupField",
        "NOC.wf.state.LookupField"
    ],
    model: "NOC.phone.phonenumber.Model",
    rowClassField: "row_class",
    search: true,
    helpId: "reference-phone-number",

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
                    text: __("State"),
                    dataIndex: "state",
                    width: 200,
                    renderer: NOC.render.Lookup("state")
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
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "profile",
                    xtype: "phone.phonenumberprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: true
                },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: true
                },
                {
                    name: "phone_range",
                    xtype: "phone.phonerange.LookupField",
                    fieldLabel: __("Range"),
                    allowBlank: true,
                    disabled: true
                },
                {
                    name: "category",
                    xtype: "phone.numbercategory.LookupField",
                    fieldLabel: __("Category"),
                    allowBlank: true
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
                    xtype: "fieldset",
                    title: __("Resource Groups"),
                    layout: "column",
                    minWidth: me.formMinWidth,
                    maxWidth: me.formMaxWidth,
                    defaults: {
                        columnWidth: 0.5,
                        padding: 10
                    },
                    collapsible: true,
                    collapsed: false,
                    items: [
                        {
                            name: "static_service_groups",
                            xtype: "gridfield",
                            columns: [
                                // {
                                //     xtype: "glyphactioncolumn",
                                //     width: 20,
                                //     sortable: false,
                                //     items: [
                                //         {
                                //             glyph: NOC.glyph.search,
                                //             tooltip: __("Show Card"),
                                //             scope: me,
                                //             handler: me.onShowResourceGroup
                                //         }
                                //     ]
                                // },
                                {
                                    dataIndex: "group",
                                    text: __("Static Service Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
                        },
                        {
                            name: "effective_service_groups",
                            xtype: "gridfield",
                            columns: [
                                {
                                    dataIndex: "group",
                                    text: __("Effective Service Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
                        },
                        {
                            name: "static_client_groups",
                            xtype: "gridfield",
                            columns: [
                                {
                                    dataIndex: "group",
                                    text: __("Static Client Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
                        },
                        {
                            name: "effective_client_groups",
                            xtype: "gridfield",
                            columns: [
                                {
                                    dataIndex: "group",
                                    text: __("Effective Client Groups"),
                                    width: 350,
                                    renderer: NOC.render.Lookup("group"),
                                    editor: {
                                        xtype: "inv.resourcegroup.LookupField"
                                    }
                                }
                            ]
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
                    title: __("By State"),
                    name: "state",
                    ftype: "lookup",
                    lookup: "wf.state"
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
