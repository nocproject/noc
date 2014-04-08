//---------------------------------------------------------------------
// gis.building application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.building.Application");

Ext.define("NOC.gis.building.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.gis.building.Model",
        "NOC.gis.building.AddressesModel",
        "NOC.gis.division.LookupField",
        "Ext.ux.form.DictField"
    ],
    model: "NOC.gis.building.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Address",
                    dataIndex: "full_path",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "full_path",
                    xtype: "displayfield",
                    fieldLabel: "Address"
                },
                {
                    name: "adm_division",
                    xtype: "gis.division.LookupField",
                    fieldLabel: "Administrative Division",
                    allowBlank: false
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: "Status",
                    allowBlank: false,
                    store: [
                        ["P", "PROJECT"],
                        ["B", "BUILDING"],
                        ["R", "READY"],
                        ["E", "EVICTED"],
                        ["D", "DEMOLISHED"]
                    ],
                    defaultValue: "R"
                },
                {
                    name: "postal_code",
                    xtype: "textfield",
                    fieldLabel: "Postal Code",
                    allowBlank: true
                },
                {
                    name: "floors",
                    xtype: "numberfield",
                    fieldLabel: "Floors",
                    allowBlank: true
                },
                {
                    name: "homes",
                    xtype: "numberfield",
                    fieldLabel: "Homes",
                    allowBlank: true
                },
                {
                    xtype: "fieldcontainer",
                    layout: "hbox",
                    items: [
                        {
                            name: "has_cellar",
                            xtype: "checkboxfield",
                            boxLabel: "Cellar"
                        },
                        {
                            name: "has_attric",
                            xtype: "checkboxfield",
                            boxLabel: "Attic"
                        },
                        {
                            name: "is_administrative",
                            xtype: "checkboxfield",
                            boxLabel: "Administrative"
                        },
                        {
                            name: "is_habitated",
                            xtype: "checkboxfield",
                            boxLabel: "Habitated"
                        }
                    ]
                },
                {
                    xtype: "dictfield",
                    name: "data",
                    fieldLabel: "Data",
                    allowBlank: true
                }
            ],
            inlines: [
                {
                    title: "Addresses",
                    model: "NOC.gis.building.AddressesModel",
                    columns: [
                        {
                            text: "Street",
                            dataIndex: "street",
                            width: 150,
                            renderer: NOC.render.Lookup("street")
                        },
                        {
                            text: "Num",
                            dataIndex: "num",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Num2",
                            dataIndex: "num2",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Num Letter",
                            dataIndex: "num_letter",
                            width: 50
                        },
                        {
                            text: "Build",
                            dataIndex: "build",
                            width: 50
                        },
                        {
                            text: "Build2",
                            dataIndex: "build2",
                            width: 50
                        },
                        {
                            text: "Build Letter",
                            dataIndex: "build_letter",
                            width: 50
                        },
                        {
                            text: "Struct",
                            dataIndex: "struct",
                            width: 50
                        },
                        {
                            text: "Struct2",
                            dataIndex: "struct2",
                            width: 50
                        },
                        {
                            text: "Struct Letter",
                            dataIndex: "struct_letter",
                            width: 50
                        },
                        {
                            text: "Estate",
                            dataIndex: "estate",
                            width: 50
                        },
                        {
                            text: "Estate2",
                            dataIndex: "estate2",
                            width: 50
                        },
                        {
                            text: "Est. Letter",
                            dataIndex: "estate_letter",
                            width: 50
                        },
                        {
                            text: "Full Number",
                            dataIndex: "text_address",
                            flex: 1
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
