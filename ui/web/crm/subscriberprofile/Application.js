//---------------------------------------------------------------------
// crm.subscriberprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriberprofile.Application");

Ext.define("NOC.crm.subscriberprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.crm.subscriberprofile.Model",
        "NOC.main.style.LookupField",
        "NOC.main.ref.glyph.LookupField"
    ],
    model: "NOC.crm.subscriberprofile.Model",
    search: true,
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Glyph"),
                    data_index: "glyph",
                    width: 25,
                    renderer: function(v) {
                        if(v !== undefined && v !== "")
                        {
                            return "<i class='" + v + "'></i>";
                        } else {
                            return "";
                        }
                    }
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    flex: 1
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    width: 150,
                    render: NOC.render.Tags
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
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    uiStyle: "expand"
                },
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "glyph",
                    xtype: "main.ref.glyph.LookupField",
                    fieldLabel: __("Icon"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "weight",
                    xtype: "numberfield",
                    fieldLabel: __("Alarm weight"),
                    allowBlank: true,
                    uiStyle: "small"
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    }
});
