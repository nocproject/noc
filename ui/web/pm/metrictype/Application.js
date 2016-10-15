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
            restUrl: new Ext.XTemplate('/pm/metrictype/{id}/json/'),
            previewName: new Ext.XTemplate('Metric Type: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    regex: /^[a-zA-Z0-9\-\_ ]+( \| [a-zA-Z0-9\-\_ ]+)*$/
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textareafield",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "scope",
                    xtype: "combobox",
                    fieldLabel: __("Scope"),
                    store: [
                        ["o", "Object"],
                        ["i", "Interface"]
                    ]
                },
                {
                    name: "measure",
                    xtype: "textfield",
                    fieldLabel: __("Measure")
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
