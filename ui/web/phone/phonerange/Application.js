//---------------------------------------------------------------------
// phone.phonerange application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
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
        "NOC.crm.supplier.LookupField"
    ],
    model: "NOC.phone.phonerange.Model",
    search: true,
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
                    flex: 1,
                    renderer: NOC.render.Lookup("supplier")
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
                    allowBlank: false
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
                    name: "from_number",
                    xtype: "textfield",
                    fieldLabel: __("From Number"),
                    allowBlank: false
                },
                {
                    name: "to_number",
                    xtype: "textfield",
                    fieldLabel: __("To Number"),
                    allowBlank: false
                },
                {
                    name: "to_allocate_numbers",
                    xtype: "checkbox",
                    boxLabel: __("Allocate Numbers")
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
