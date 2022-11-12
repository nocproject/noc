//---------------------------------------------------------------------
// main.imagestore application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.imagestore.Application");

Ext.define("NOC.main.imagestore.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.imagestore.Model"
    ],
    model: "NOC.main.imagestore.Model",
    search: true,
    helpId: "reference-handler",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 150
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "meduim"
                },
                {
                    name: "content_type",
                    xtype: "textfield",
                    fieldLabel: __("Content Type"),
                    allowBlank: false,
                    uiStyle: "meduim"
                },
                {
                    layout: "hbox",
                    border: false,
                    items: [
                        {
                            xtype: "displayfield",
                            name: "name",
                            fieldLabel: __("File name"),
                            allowBlank: true,
                            width: 400
                        },
                        {
                            xtype: "filefield",
                            name: "file",
                            flex: 1,
                            buttonOnly: true,
                            hideLabel: true,
                            buttonText: __("Select File..."),
                            listeners: {
                                change: me.setAttachmentName
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    setAttachmentName: function(field, value) {
        var filename = value.replace(/(^.*([\\/]))?/, "");
        field.previousSibling().setValue(filename)
    },
});
