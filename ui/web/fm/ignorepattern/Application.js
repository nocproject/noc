//---------------------------------------------------------------------
// fm.ignorepattern application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignorepattern.Application");

Ext.define("NOC.fm.ignorepattern.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.ignorepattern.Model"
    ],
    model: "NOC.fm.ignorepattern.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Source"),
                    dataIndex: "source",
                    width: 75
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Pattern"),
                    dataIndex: "pattern",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "source",
                    xtype: "combobox",
                    fieldLabel: __("Source"),
                    allowBlank: false,
                    store: [
                        ["syslog", "SYSLOG"],
                        ["SNMP Trap", "SNMP Trap"]
                    ]
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "pattern",
                    xtype: "textfield",
                    fieldLabel: __("Pattern (RE)"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    onCmd_from_event: function(data) {
        var me = this;
        Ext.Ajax.request({
            url: "/fm/ignorepattern/from_event/" + data.id + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var me = this,
                    data = Ext.decode(response.responseText);
                me.newRecord(data);
            },
            failure: function() {
                NOC.error(__("Failed to create ignore pattern from event"));
            }
        });
    },

});
