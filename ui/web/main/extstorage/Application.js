//---------------------------------------------------------------------
// main.extstorage application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.extstorage.Application");

Ext.define("NOC.main.extstorage.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.extstorage.Model"
    ],
    model: "NOC.main.extstorage.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Proto"),
                    dataIndex: "url",
                    width: 100,
                    renderer: function(value) {
                        var i = value.indexOf("://");
                        if(i === -1) {
                            return "OSFS"
                        } else {
                            return value.substring(0, i)
                        }
                    }
                },
                {
                    text: __("Cfg. Mirror"),
                    dataIndex: "enable_config_mirror",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Beef"),
                    dataIndex: "enable_beef",
                    width: 50,
                    renderer: NOC.render.Bool
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
                    name: "url",
                    xtype: "textfield",
                    fieldLabel: __("URL"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "enable_config_mirror",
                    xtype: "checkbox",
                    boxLabel: __("Config Mirror")
                },
                {
                    name: "enable_beef",
                    xtype: "checkbox",
                    boxLabel: __("Beef")
                }
            ]
        });
        me.callParent();
    }
});
