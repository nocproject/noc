//---------------------------------------------------------------------
// project.project application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.Application");

Ext.define("NOC.project.project.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.project.project.Model",
        "NOC.main.glyph.LookupField",
        "NOC.main.ref.soposition.LookupField",
        "NOC.main.ref.soform.LookupField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.project.project.Model",
    search: true,
    initComponent: function() {
        var me = this;
        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        Ext.apply(me, {
            formToolbar: [
                me.cardButton
            ],
            columns: [
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 150
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: __("Shape Overlay"),
                    layout: "hbox",
                    defaults: {
                        padding: 4
                    },
                    items: [
                        {
                            name: "shape_overlay_glyph",
                            xtype: "main.glyph.LookupField",
                            fieldLabel: __("Glyph"),
                            allowBlank: true
                        },
                        {
                            name: "shape_overlay_position",
                            xtype: "main.ref.soposition.LookupField",
                            fieldLabel: __("Position"),
                            allowBlank: true
                        },
                        {
                            name: "shape_overlay_form",
                            xtype: "main.ref.soform.LookupField",
                            fieldLabel: __("Form"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/project/" + me.currentRecord.get("id") + "/"
            );
        }
    }
});
