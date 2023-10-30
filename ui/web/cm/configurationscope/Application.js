//---------------------------------------------------------------------
// cm.configurationscope application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.configurationscope.Application");

Ext.define("NOC.cm.configurationscope.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.cm.configurationscope.Model",
        "NOC.main.ref.modelid.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.cm.configurationscope.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/cm/configurationscope/{id}/json/'),
            previewName: new Ext.XTemplate('Configuration Scope: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 350
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    labelAlign: "top",
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID"),
                    labelAlign: "top",
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    labelAlign: "top",
                    allowBlank: true
                },
                {
                    text: __('ModelID'),
                    dataIndex: 'model_id',
                    renderer: NOC.render.Lookup('model_id'),
                    editor: 'main.ref.modelid.LookupField',
                    width: 150
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
