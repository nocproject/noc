//---------------------------------------------------------------------
// inv.connectiontype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectiontype.Application");

Ext.define("NOC.inv.connectiontype.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "Ext.ux.form.GridField",
        "Ext.ux.form.ModelDataField",
        "NOC.inv.connectiontype.LookupField",
        "NOC.core.StringListField"
    ],
    model: "NOC.inv.connectiontype.Model",
    search: true,
    filters: [
        {
            title: "By Is Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ],
    //
    initComponent: function() {
        var me = this;
        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/inv/connectiontype/{{id}}/json/",
            previewName: "Connection Type: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        //
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    width: 300,
                    dataIndex: "name"
                },
                {
                    text: "Builtin",
                    width: 50,
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool
                },
                {
                    text: "Description",
                    flex: 1,
                    dataIndex: "description"
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
                    name: "extend",
                    xtype: "inv.connectiontype.LookupField",
                    fieldLabel: "Extend",
                    allowBlank: true
                },
                {
                    name: "has_gender",
                    xtype: "checkboxfield",
                    boxLabel: "Has Gender"
                },
                {
                    name: "multi_connection",
                    xtype: "checkboxfield",
                    boxLabel: "Multi Connection"
                },
                {
                    name: "data",
                    xtype: "modeldatafield",
                    fieldLabel: "Model Data"
                },
                {
                    name: "c_group",
                    xtype: "stringlistfield",
                    fieldLabel: "Compatible groups"
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
