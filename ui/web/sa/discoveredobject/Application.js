//---------------------------------------------------------------------
// sa.service application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.Application");

Ext.define("NOC.sa.discoveredobject.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.StateField",
        "NOC.sa.discoveredobject.Model",
        "NOC.main.remotesystem.LookupField",
        "NOC.main.pool.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.core.label.LabelField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.sa.discoveredobject.Model",
    search: true,
    helpId: "reference-service",

    initComponent: function () {
        var me = this;

        Ext.apply(me, {
            columns: [
                // {
                //     text: __("ID"),
                //     dataIndex: "id",
                //     width: 160
                // },
                //{
                //    text: __("Rule"),
                //    dataIndex: "rule",
                //    width: 200,
                //    renderer: NOC.render.Lookup("rule")
                //},
                {
                    text: "IP",
                    dataIndex: "address",
                    width: 100
                },
                {
                    text: "Pool",
                    dataIndex: "pool",
                    width: 100,
                    renderer: NOC.render.Lookup("pool")
                },
                {
                    text: "Hostname",
                    dataIndex: "hostname",
                    width: 150
                },
                // {
                //     text: "Name",
                //     dataIndex: "name",
                //     width: 200
                // },
                {
                    text: "Description",
                    dataIndex: "description",
                    width: 200
                },
                {
                    text: __("State"),
                    dataIndex: "state",
                    width: 200,
                    renderer: NOC.render.Lookup("state")
                },
                {
                    text: __("IsDrt"),
                    dataIndex: "is_dirty",
                    width: 30,
                    renderer: NOC.render.Bool,
                    align: "center"
                },
                {
                    text: __("Sources"),
                    dataIndex: "sources",
                    width: 150
                },
                {
                    text: __("check"),
                    dataIndex: "checks",
                    width: 200
                }
            ],

            fields: [
                // {
                //     name: "rule",
                //     xtype: "sa.serviceprofile.LookupField",
                //     fieldLabel: __("Rule"),
                //     allowBlank: false
                // },
                {
                    name: "state",
                    xtype: "statefield",
                    fieldLabel: __("State"),
                    allowBlank: true
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    query: {
                        "allow_models": ["sa.ManagedObject"]
                    },
                }
            ]
        });
        me.callParent();
    },

    filters: [
        {
            title: __("By State"),
            name: "state",
            ftype: "lookup",
            lookup: "wf.state"
        }
    ]
});
