//---------------------------------------------------------------------
// pm.scale application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.scale.Application");

Ext.define("NOC.pm.scale.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.scale.Model"
    ],
    model: "NOC.pm.scale.Model",
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate("/pm/scale/{id}/json/"),
            previewName: new Ext.XTemplate("Scale: {name}")
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 50
                },
                {
                    text: __("Scale"),
                    dataIndex: "exp",
                    flex: 1,
                    renderer: function (value, metaData, record) {
                        let exp = record.get("exp");
                        if(exp === 0) {
                            return "1"
                        } else {
                            return record.get("base") + "<sup>" + record.get("exp") + "</sup>";
                        }
                    }
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "label",
                    xtype: "textfield",
                    fieldLabel: __("Label"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "base",
                    xtype: "combobox",
                    fieldLabel: __("Base"),
                    store: [
                        [2, "2"],
                        [10, "10"]
                    ],
                    allowBlank: false
                },
                {
                    name: "exp",
                    xtype: "numberfield",
                    fieldLabel: __("Exponent"),
                    allowBlank: false
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