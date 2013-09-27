//---------------------------------------------------------------------
// inv.objectmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.Application");

Ext.define("NOC.inv.objectmodel.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "Ext.ux.form.GridField",
        "Ext.ux.form.ModelDataField",
        "NOC.inv.objectmodel.Model",
        "NOC.inv.vendor.LookupField",
        "NOC.inv.connectiontype.LookupField"
    ],
    model: "NOC.inv.objectmodel.Model",
    search: true,
    filters: [
        {
            title: "By Is Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/inv/objectmodel/{{id}}/json/",
            previewName: "Object Model: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        //
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 300
                },
                {
                    text: "Vendor",
                    dataIndex: "vendor",
                    renderer: NOC.render.Lookup("vendor"),
                    width: 150
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
                    allowBlank: false
                },
                {
                    name: "is_builtin",
                    xtype: "checkboxfield",
                    boxLabel: "Is Builtin"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "vendor",
                    xtype: "inv.vendor.LookupField",
                    fieldLabel: "Vendor",
                    allowBlank: false
                },
                {
                    name: "data",
                    xtype: "modeldatafield",
                    fieldLabel: "Model Data"
                },
                {
                    name: "connections",
                    xtype: "gridfield",
                    fieldLabel: "Connections",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name",
                            editor: "textfield",
                            width: 150
                        },
                        {
                            text: "Connection Type",
                            dataIndex: "type",
                            editor: "inv.connectiontype.LookupField",
                            width: 200,
                            renderer: NOC.render.Lookup("type")
                        },
                        {
                            text: "Group",
                            dataIndex: "group",
                            editor: "textfield",
                            width: 100
                        },
                        {
                            text: "Direction",
                            dataIndex: "direction",
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["i", "Inner"],
                                    ["o", "Outer"],
                                    ["s", "Connection"]
                                ]
                            },
                            width: 70
                        },
                        {
                            text: "Gender",
                            dataIndex: "gender",
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["m", "Male"],
                                    ["f", "Female"],
                                    ["s", "Genderless"]
                                ]
                            },
                            width: 70
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: "JSON",
                    glyph: NOC.glyph.file,
                    tooltip: "Show JSON",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
