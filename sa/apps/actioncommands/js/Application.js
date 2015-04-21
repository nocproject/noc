//---------------------------------------------------------------------
// sa.actioncommands application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.actioncommands.Application");

Ext.define("NOC.sa.actioncommands.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.actioncommands.Model",
        "NOC.sa.action.LookupField",
        "NOC.main.ref.profile.LookupField"
    ],
    model: "NOC.sa.actioncommands.Model",
    search: true,
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/sa/actioncommands/{{id}}/json/",
            previewName: "Action Commands: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Profile",
                    dataIndex: "profile",
                    width: 100
                },
                {
                    text: "Preference",
                    dataIndex: "preference",
                    width: 100,
                    align: "right"
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: "UUID"
                },
                {
                    name: "action",
                    xtype: "sa.action.LookupField",
                    fieldLabel: "Action",
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    uiStyle: "extra"
                },
                {
                    name: "profile",
                    xtype: "main.ref.profile.LookupField",
                    fieldLabel: "Profile",
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "config_mode",
                    xtype: "checkbox",
                    boxLabel: "Config. Mode"
                },
                {
                    name: "preference",
                    xtype: "numberfield",
                    fieldLabel: "Preference",
                    allowBlank: true
                },
                {
                    name: "timeout",
                    xtype: "numberfield",
                    fieldLabel: "Timeout",
                    allowBlank: true
                },
                {
                    name: "match",
                    xtype: "gridfield",
                    fieldLabel: "Match",
                    columns: [
                        {
                            text: "Platform (Regex)",
                            dataIndex: "platform_re",
                            editor: "textfield"
                        },
                        {
                            text: "Version (Regex)",
                            dataIndex: "version_re",
                            editor: "textfield"
                        }
                    ]
                },
                {
                    name: "commands",
                    xtype: "textarea",
                    fieldLabel: "Commands",
                    allowBlank: false
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

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
