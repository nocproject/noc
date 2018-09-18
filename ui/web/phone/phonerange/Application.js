//---------------------------------------------------------------------
// phone.phonerange application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonerange.Application");

Ext.define("NOC.phone.phonerange.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.phone.phonerange.Model",
        "NOC.phone.dialplan.LookupField",
        "NOC.phone.phonerangeprofile.LookupField",
        "NOC.project.project.LookupField",
        "NOC.crm.supplier.LookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.inv.resourcegroup.LookupField"
    ],
    model: "NOC.phone.phonerange.Model",
    search: true,
    helpId: "reference-phonerange",
    rowClassField: "row_class",

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
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("From Number"),
                    dataIndex: "from_number",
                    width: 100
                },
                {
                    text: __("To Number"),
                    dataIndex: "to_number",
                    width: 100
                },
                {
                    text: __("State"),
                    dataIndex: "state",
                    width: 200,
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("Allocated"),
                    dataIndex: "to_allocate_numbers",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Total"),
                    dataIndex: "total_numbers",
                    align: "right",
                    width: 50
                },
                {
                    text: __("Supplier"),
                    dataIndex: "supplier",
                    width: 100,
                    renderer: NOC.render.Lookup("supplier")
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
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "from_number",
                    xtype: "textfield",
                    regex: /^\d+$/,
                    fieldLabel: __("From Number"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "to_number",
                    xtype: "textfield",
                    regex: /^\d+$/,
                    fieldLabel: __("To Number"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "profile",
                    xtype: "phone.phonerangeprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: false
                },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: true
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: __("Project"),
                    allowBlank: true
                },
                {
                    name: "supplier",
                    xtype: "crm.supplier.LookupField",
                    fieldLabel: __("Supplier"),
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
                },
                {
                    name: "to_allocate_numbers",
                    xtype: "checkbox",
                    boxLabel: __("Allocate Numbers")
                },
            ],

            formToolbar: [
                me.cardButton
            ]
        });

        me.currentQuery = {
            "parent__exists": false
        };

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
            name: "parent",
            ftype: "tree",
            lookup: "phone.phonerange"
        },
        {
            title: __("By Supplier"),
            name: "supplier",
            ftype: "lookup",
            lookup: "crm.supplier"
        },
        {
            title: __("By Project"),
            name: "project",
            ftype: "lookup",
            lookup: "project.project"
        }
    ],
    //
    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/phonerange/" + me.currentRecord.get("id") + "/"
            );
        }
    },
    levelFilter: {
        icon: NOC.glyph.level_down,
        color: NOC.colors.level_down,
        filter: 'parent',
        tooltip: __('Parent filter')
    }
});
