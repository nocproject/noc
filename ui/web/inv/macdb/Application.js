//---------------------------------------------------------------------
// inv.macdb application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.Application");

Ext.define("NOC.inv.macdb.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.macdb.MACLogForm",
        "NOC.inv.macdb.Model",
        "NOC.main.style.LookupField",
        "NOC.main.pool.LookupField",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.sa.managedobject.LookupField"
    ],
    model: "NOC.inv.macdb.Model",
    search: true,
    searchPlaceholder: "insert MAC address to search",
    searchTooltip: __("Insert MAC address to this field one of format:<li>FULL: AA:AA:AA:AA:AA:AA</li><li>Left part: AA:AA:</li><li>Right part: :AA:AA</li>"),
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
                    text: __("Mac Address"),
                    dataIndex: "mac",
                    width: 110
                },
                {
                    text: __("L2 Domain"),
                    dataIndex: "l2_domain",
                    renderer: NOC.render.Lookup("l2_domain"),
                    flex: 1
                },
                {
                    text: __("Pool"),
                    dataIndex: "pool",
                    renderer: NOC.render.Lookup("pool"),
                    flex: 1
                },
                {
                    text: __("Object Profile"),
                    dataIndex: "object_profile",
                    renderer: NOC.render.Lookup("object_profile"),
                    flex: 1
                },
                {
                    text: __("Vlan"),
                    dataIndex: "vlan",
                    width: 40
                },
                {
                    flex: 1,
                    text: __("Managed Object"),
                    renderer: NOC.render.Lookup("managed_object"),
                    dataIndex: "managed_object"
                },
                {
                    flex: 1,
                    text: __("Interface"),
                    renderer: function(v) {
                        var array = v.split(":");
                        return array[1];
                    },
                    dataIndex: "interface__label"
                },
                {
                    flex: 1,
                    text: __("Description"),
                    dataIndex: "description"
                },
                {
                    text: __("Last Changed"),
                    dataIndex: "last_changed",
                    width: 150
                }
            ],
            fields: [
            ]

        });

        me.callParent();
    },

    filters: [
        {
            title: __("By Profile"),
            name: "interface_profile",
            ftype: "lookup",
            lookup: "inv.interfaceprofile"
        },
        {
            title: __("By Object"),
            name: "managed_object",
            ftype: "lookup",
            lookup: "sa.managedobject"
        }
    ],

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
