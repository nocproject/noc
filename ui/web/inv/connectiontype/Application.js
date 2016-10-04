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
        "Ext.ux.form.ModelDataField",
        "NOC.inv.connectiontype.LookupField",
        "NOC.inv.connectiontype.templates.Test"
    ],
    model: "NOC.inv.connectiontype.Model",
    search: true,
    treeFilter: "category",
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
        // Test panel
        me.testPanel = Ext.create("NOC.core.TemplatePreview", {
            app: me,
            previewName: "Compatible connections for {{name}}",
            template: me.templates.Test
        });
        me.ITEM_TEST = me.registerItem(me.testPanel);
        //
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    width: 300,
                    dataIndex: "name"
                },
                {
                    text: __("Builtin"),
                    width: 50,
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    sortable: false
                },
                {
                    text: __("Genders"),
                    width: 50,
                    dataIndex: "genders"
                },
                {
                    text: __("Description"),
                    flex: 1,
                    dataIndex: "description"
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    boxLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description")
                },
                {
                    name: "extend",
                    xtype: "inv.connectiontype.LookupField",
                    fieldLabel: __("Extend"),
                    allowBlank: true
                },
                {
                    name: "genders",
                    xtype: "combobox",
                    fieldLabel: __("Genders"),
                    store: [
                        ["s", "Genderless"],
                        ["ss", "Genderless, 2 or more"],
                        ["m", "Only male"],
                        ["f", "Only female"],
                        ["mmf", "Males/Female"],
                        ["mf", "Male/Female"],
                        ["mff", "Male/Females"]
                    ],
                    allowBlank: false
                },
                {
                    name: "data",
                    xtype: "modeldatafield",
                    fieldLabel: __("Model Data")
                },
                {
                    name: "c_group",
                    xtype: "stringlistfield",
                    fieldLabel: __("Compatible groups")
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                },
                {
                    text: __("Test"),
                    glyph: NOC.glyph.question,
                    tooltip: __("Test compatible types"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onTest
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
    },
    //
    onTest: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/connectiontype/" + me.currentRecord.get("id") + "/compatible/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.showItem(me.ITEM_TEST).preview(me.currentRecord, {data: data});
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    }
});
