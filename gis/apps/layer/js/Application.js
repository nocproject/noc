//---------------------------------------------------------------------
// gis.layer application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.layer.Application");

Ext.define("NOC.gis.layer.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.gis.layer.Model",
        "Ext.ux.form.ColorField"
    ],
    model: "NOC.gis.layer.Model",
    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/gis/layer/{{id}}/json/",
            previewName: "Layer: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Code",
                    dataIndex: "code",
                    width: 100
                },
                {
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50
                },
                {
                    text: "Min Zoom",
                    dataIndex: "min_zoom",
                    width: 50,
                    align: "right"
                },
                {
                    text: "Max Zoom",
                    dataIndex: "max_zoom",
                    width: 50,
                    align: "right"
                },
                {
                    text: "Def. Zoom",
                    dataIndex: "default_zoom",
                    width: 50,
                    align: "right"
                },
                {
                    text: "Color",
                    dataIndex: "stroke_color",
                    width: 50,
                    renderer: me.renderStyle
                }
            ],
            fields: [
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    xtype: "textfield",
                    name: "code",
                    fieldLabel: "Code",
                    allowBlank: false
                },
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: "UUID"
                },
                {
                    xtype: "textarea",
                    name: "description",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: "Zoom",
                    layout: "hbox",
                    items: [
                        {
                            xtype: "numberfield",
                            name: "min_zoom",
                            fieldLabel: "Min",
                            minValue: 0,
                            maxValue: 19
                        },
                                                {
                            xtype: "numberfield",
                            name: "max_zoom",
                            fieldLabel: "Max",
                            minValue: 0,
                            maxValue: 19
                        },
                        {
                            xtype: "numberfield",
                            name: "default_zoom",
                            fieldLabel: "Default",
                            minValue: 0,
                            maxValue: 19
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: "Style",
                    items: [
                        {
                            name: "stroke_color",
                            xtype: "colorfield",
                            fieldLabel: "Stroke Color",
                            allowBlank: false
                        },
                        {
                            name: "fill_color",
                            xtype: "colorfield",
                            fieldLabel: "Fill Color",
                            allowBlank: false
                        }
                    ]
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
    renderStyle: function(value, meta, record) {
        return "<span style='padding: 2px; border: 1px solid #" + record.get("stroke_color") + "; background-color: #" + record.get("fill_color") + "'>&nbsp;&nbsp;&nbsp;&nbsp;</span>";
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
