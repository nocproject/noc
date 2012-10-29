//---------------------------------------------------------------------
// inv.macdb application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.Application");

// @todo: filtering macs based on managed objects

Ext.define("NOC.inv.macdb.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.macdb.Model",
        "NOC.main.style.LookupField"
    ],
    model: "NOC.inv.macdb.Model",
    search: true,
    canCreate: false,
    rowClassField: "row_class",

    filters: [
    ],

    //
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Mac Address",
                    dataIndex: "mac",
                    width: 110,
                    renderer: NOC.render.Clickable,
                    onClick: me.onMACCellClick
                },
                {
                    text: "Vlan",
                    dataIndex: "vlan",
                    width: 40
                },
                {
                    flex: 1,
                    text: "Managed Object",
                    dataIndex: "managed_object__label"
                },
                {
                    flex: 1,
                    text: "Interface",
                    dataIndex: "interface__label"
                },
                {
                    text: "Last Changed",
                    dataIndex: "last_changed",
                    width: 150
                }
            ],
            fields: [
            ]

        });

        me.callParent();
    },

    // Show mac log window
    showMACLog: function(record) {
        var me = this;
        me.currentMAC = record.get("mac");
        Ext.Ajax.request({
            url: "/inv/macdb/" + record.get("mac") + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(!r) {
                    NOC.info("No MAC history found");
                } else {
                    Ext.create("NOC.inv.macdb.MACLogForm", {
                        data: r,
                        title: Ext.String.format("MAC {0} history",
                               me.currentMAC)
                    });
                }
            },
            failure: function() {
                NOC.error("Failed to get MAC history");
            }
        });
    },

    //
    onMACCellClick: function(record) {
        var me = this;
        me.showMACLog(record);
    }
});
