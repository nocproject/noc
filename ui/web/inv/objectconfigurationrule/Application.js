//---------------------------------------------------------------------
// inv.objectconfigurationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectconfigurationrule.Application");

Ext.define("NOC.inv.objectconfigurationrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.core.StringListField",
        "NOC.core.tagfield.Tagfield",
        "NOC.inv.objectconfigurationrule.Model",
        "NOC.inv.connectiontype.LookupField",
        "NOC.inv.protocol.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.objectconfigurationrule.Model",
    search: true,

    actions: [
        {
            title: __("Get JSON"),
            action: "json",
            glyph: NOC.glyph.file,
            resultTemplate: "JSON"
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/objectconfigurationrule/{id}/json/'),
            previewName: new Ext.XTemplate('Configuration Rule: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    width: 50,
                    renderer: NOC.render.Bool,
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
                    fieldLabel: __("Name"),
                    xtype: "textfield",
                    allowBlank: false
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description")
                },
                {
                    name: "slot_rules",
                    xtype: "gridfield",
                    fieldLabel: __("Slot Rules"),
                    columns: [
                        {
                            text: __("Match Slot"),
                            dataIndex: "match_slot",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Connection Type"),
                            dataIndex: "match_connection_type",
                            editor: "inv.connectiontype.LookupField",
                            width: 200,
                            renderer: NOC.render.Lookup("match_connection_type")
                        },
                        {
                            text: __("Protocols"),
                            dataIndex: "match_protocols",
                            width: 200,
                            editor: {
                                xtype: "core.tagfield",
                                url: "/cm/protocol/lookup/"
                            }
                            renderer: NOC.render.Lookup("match_protocols")
                        },
                        {
                            text: __("Allow Params"),
                            dataIndex: "allowed_params",
                            width: 200,
                            editor: {
                                xtype: "core.tagfield",
                                url: "/cm/configurationparam/lookup/"
                            }
                            renderer: NOC.render.Lookup("allowed_params")
                        },
                        {
                            text: __("Deny Params"),
                            dataIndex: "deny_params",
                            width: 200,
                            editor: {
                                xtype: "core.tagfield",
                                url: "/cm/configurationparam/lookup/"
                            }
                            renderer: NOC.render.Lookup("allowed_params")
                        }
                    ]
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
            title: __("By Is Builtin"),
            name: "is_builtin",
            ftype: "boolean"
        }
    ],

    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
