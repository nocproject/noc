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
                    width: 110
                },
                {
                    text: "VC Domain",
                    dataIndex: "vc_domain",
                    renderer: NOC.render.Lookup("vc_domain"),
                    flex: 1
                },
                {
                    text: "Vlan",
                    dataIndex: "vlan",
                    width: 40
                },
                {
                    flex: 1,
                    text: "Managed Object",
                    renderer: NOC.render.Lookup("managed_object"),
                    dataIndex: "managed_object"
                },
                {
                    flex: 1,
                    text: "Interface",
                    renderer: function(v) {
                        var array = v.split(":");
                        return array[1];
                    },
                    dataIndex: "interface__label"
                },
                {
                    flex: 1,
                    text: "Description",
                    dataIndex: "description"
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

    createForm: function() {
        var me = this;
        me.form = Ext.create("NOC.inv.macdb.MACLogForm", {app: me});
        return me.form;
    },

    onEditRecord: function(record) {
        var me = this;
        me.showItem(me.ITEM_FORM).preview(record);
    }
});
