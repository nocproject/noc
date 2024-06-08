//---------------------------------------------------------------------
// inv.protocol application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.protocol.Application");

Ext.define("NOC.inv.protocol.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.core.label.LabelField",
        "NOC.inv.protocol.Model",
        "NOC.inv.technology.LookupField",
        "NOC.inv.modelinterface.LookupField",
        "NOC.main.ref.protocoldiscriminatorsource.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.protocol.Model",
    search: true,

    initComponent: function () {
        var me = this;

        // me.cardButton = Ext.create("Ext.button.Button", {
        //     text: __("Card"),
        //     glyph: NOC.glyph.eye,
        //     scope: me,
        //     handler: me.onCard
        // });

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/inv/protocol/{id}/json/'),
            previewName: new Ext.XTemplate('Protocol: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Technology"),
                    dataIndex: "technology",
                    width: 150,
                    renderer: NOC.render.Lookup("technology")
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 100
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    width: 30,
                    renderer: NOC.render.Bool,
                    sortable: false
                },
                {
                    text: __("Connection Schema"),
                    dataIndex: "connection_schema",
                    width: 100
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID"),
                    allowBlank: true
                },
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: false
                },
                {
                    name: "technology",
                    xtype: "inv.technology.LookupField",
                    fieldLabel: __("Technology"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "connection_schema",
                    xtype: "combobox",
                    fieldLabel: __("Connection Schema"),
                    allowBlank: true,
                    labelWidth: 200,
                    defaultValue: "BD",
                    store: [
                        ["U", __("Unidirectional")],
                        ["BO", __("Bidirectional over One Connection")],
                        ["BD", __("Bidirectional over Differ Connection")]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "data",
                    fieldLabel: __("Data"),
                    xtype: "gridfield",
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Interface"),
                            dataIndex: "interface",
                            editor: {
                                xtype: "inv.modelinterface.LookupField",
                                forceSelection: true,
                                valueField: "label"
                            }
                        },
                        {
                            text: __("Key"),
                            dataIndex: "attr",
                            editor: "textfield"
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            editor: "textfield"
                        }

                    ]
                },
                {
                    name: "discriminator",
                    xtype: "combobox",
                    fieldLabel: __("Discriminator"),
                    allowBlank: true,
                    store: [
                        ["loader", __("From Loader")],
                        ["lambda", __("Optical Lambda")],
                        ["odu", __("OTN ODU")],
                        ["vlan", __("VLAN")]
                    ],
                    uiStyle: "medium"
                },
                {
                    name: "discriminator_loader",
                    xtype: "main.ref.protocoldiscriminatorsource.LookupField",
                    fieldLabel: __("Discriminator Source"),
                    allowBlank: true
                },
                {
                    name: "discriminator_default",
                    xtype: "textfield",
                    fieldLabel: __("Discriminator Default"),
                    allowBlank: true
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
            ],

            filters: [
                {
                    title: __("By Technology"),
                    name: "technology",
                    ftype: "lookup",
                    lookup: "inv.technology"
                }
            ]
        });
        me.callParent();
    },

    //
    // onCard: function() {
    //     var me = this;
    //     if(me.currentRecord) {
    //         window.open(
    //             "/api/card/view/technology/" + me.currentRecord.get("id") + "/"
    //         );
    //     }
    // },

    onJSON: function () {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
