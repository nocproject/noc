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
            restUrl: new Ext.XTemplate('/sa/actioncommands/{id}/json/'),
            previewName: new Ext.XTemplate('Action Commands: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 100
                },
                {
                    text: __("Preference"),
                    dataIndex: "preference",
                    width: 100,
                    align: "right"
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "action",
                    xtype: "sa.action.LookupField",
                    fieldLabel: __("Action"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    uiStyle: "extra"
                },
                {
                    name: "profile",
                    xtype: "main.ref.profile.LookupField",
                    fieldLabel: __("Profile"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "config_mode",
                    xtype: "checkbox",
                    boxLabel: __("Config. Mode")
                },
                {
                    name: "preference",
                    xtype: "numberfield",
                    fieldLabel: __("Preference"),
                    allowBlank: true
                },
                {
                    name: "timeout",
                    xtype: "numberfield",
                    fieldLabel: __("Timeout"),
                    allowBlank: true
                },
                {
                    name: "match",
                    xtype: "gridfield",
                    fieldLabel: __("Match"),
                    columns: [
                        {
                            text: __("Platform (Regex)"),
                            dataIndex: "platform_re",
                            editor: "textfield"
                        },
                        {
                            text: __("Version (Regex)"),
                            dataIndex: "version_re",
                            editor: "textfield"
                        }
                    ]
                },
                {
                    name: "commands",
                    xtype: "textarea",
                    fieldLabel: __("Commands"),
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

    filters: [
        {
            title: __("By SA Profile"),
            name: "profile",
            ftype: "lookup",
            lookup: "main.ref.profile"
        },
        {
            title: __("By Action"),
            name: "action",
            ftype: "lookup",
            lookup: "sa.action"
        }
    ],

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
