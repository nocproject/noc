//---------------------------------------------------------------------
// pm.metrictype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metrictype.Application");

Ext.define("NOC.pm.metrictype.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metrictype.Model"
    ],
    model: "NOC.pm.metrictype.Model",
    search: true,
    treeFilter: "category",
    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/pm/metrictype/{{id}}/json/",
            previewName: "Metric Type: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
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
                    regex: /^[a-zA-Z0-9\-\_ ]+( \| [a-zA-Z0-9\-\_ ]+)*$/
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: "UUID"
                },
                {
                    name: "description",
                    xtype: "textareafield",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "scope",
                    xtype: "combobox",
                    fieldLabel: "Scope",
                    store: [
                        ["o", "Object"],
                        ["i", "Interface"]
                    ]
                },
                {
                    name: "measure",
                    xtype: "textfield",
                    fieldLabel: "Measure"
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
