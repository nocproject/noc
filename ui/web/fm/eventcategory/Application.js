//---------------------------------------------------------------------
// fm.eventcategory application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.eventcategory.Application");

Ext.define("NOC.fm.eventcategory.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.fm.eventcategory.LookupField",
        "NOC.fm.eventcategory.Model"
    ],
    model: "NOC.fm.eventcategory.Model",
    search: true,

    initComponent: function() {
        var me = this;
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/fm/eventcategory/{id}/json/'),
            previewName: new Ext.XTemplate('MIB Preference: {name}')
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
                    text: __("Description"),
                    dataIndex: "description",
                    width: 100
                },
                {
                    text: __("Level"),
                    dataIndex: "level",
                    width: 100
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
                },
                {
                    text: __("Parent"),
                    dataIndex: "parent",
                    renderer: NOC.render.Lookup("parent"),
                    width: 150,
                    hidden: true
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
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                  name: "parent",
                  xtype: "fm.eventcategory.LookupField",
                  fieldLabel: __("Parent"),
                  allowBlank: true,
                },
                {
                    name: "level",
                    xtype: "combobox",
                    fieldLabel: __("Level"),
                    allowBlank: false,
                    store: [
                        [1, __("Context (Lvl. 1)")],
                        [2, __("Object (Lvl. 2)")],
                        [3, __("Disposition (Lvl. 3)")]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "vars",
                    xtype: "gridfield",
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: __("Type"),
                            dataIndex: "type",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    "str",
                                    "int", "float",
                                    "ipv4_address", "ipv6_address", "ip_address",
                                    "ipv4_prefix", "ipv6_prefix", "ip_prefix",
                                    "mac", "interface_name", "oid"
                                ]
                            }
                        },
                        {
                            text: __("Required"),
                            dataIndex: "required",
                            width: 50,
                            editor: "checkboxfield",
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Suppression"),
                            dataIndex: "match_suppress",
                            width: 50,
                            editor: "checkboxfield",
                            renderer: NOC.render.Bool
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description",
                            flex: 1,
                            editor: "textfield"
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
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
