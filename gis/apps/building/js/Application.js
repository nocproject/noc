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
        "NOC.gis.street.LookupField",
        "Ext.ux.form.DictField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.gis.building.Model",
    search: true,
    treeFilter: "adm_division",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Address",
                    dataIndex: "full_path",
                    flex: 1
                },
                {
                    text: "Floors",
                    dataIndex: "floors",
                    width: 75,
                    align: "right"
                },
                {
                    text: "Homes",
                    dataIndex: "homes",
                    width: 75,
                    align: "right"
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
                },
                {
                    xtype: "gridfield",
                    name: "entrances",
                    fieldLabel: "Entrances",
                    allowBlank: true,
                    columns: [
                        {
                            text: "Number",
                            dataIndex: "number",
                            width: 75,
                            editor: "textfield"
                        },
                        {
                            text: "First Floor",
                            dataIndex: "first_floor",
                            width: 75,
                            editor: "textfield"
                        },
                        {
                            text: "Last Floor",
                            dataIndex: "last_floor",
                            width: 75,
                            editor: "textfield"
                        },
                        {
                            text: "First Home",
                            dataIndex: "first_home",
                            width: 75,
                            editor: "textfield"
                        },
                        {
                            text: "Last Home",
                            dataIndex: "last_home",
                            width: 75,
                            editor: "textfield"
                        }
                    ],
                    toolbar: [
                        {
                            text: "Fill Entrances",
                            glyph: NOC.glyph.plus_sign_alt,
                            scope: me,
                            handler: me.onFillEntrances
                        }
                    ]
                }
            ],
            inlines: [
                {
                    title: "Addresses",
                    model: "NOC.gis.building.AddressesModel",
                    columns: [
                        {
                            text: "Primary",
                            dataIndex: "is_primary",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: {
                                xtype: "checkboxfield",
                                listeners: {
                                    scope: me,
                                    change: me.onPrimaryAddressChange
                                }
                            }
                        },
                        {
                            text: "Street",
                            dataIndex: "street",
                            width: 150,
                            renderer: NOC.render.Lookup("street"),
                            editor: "gis.street.LookupField"
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
                            width: 50,
                            editor: "textfield"
                        },
                        {
                            text: "Build",
                            dataIndex: "build",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Build2",
                            dataIndex: "build2",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Build Letter",
                            dataIndex: "build_letter",
                            width: 50,
                            editor: "textfield"
                        },
                        {
                            text: "Struct",
                            dataIndex: "struct",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Struct2",
                            dataIndex: "struct2",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Struct Letter",
                            dataIndex: "struct_letter",
                            width: 50,
                            editor: "textfield"
                        },
                        {
                            text: "Estate",
                            dataIndex: "estate",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Estate2",
                            dataIndex: "estate2",
                            width: 50,
                            editor: "numberfield"
                        },
                        {
                            text: "Est. Letter",
                            dataIndex: "estate_letter",
                            width: 50,
                            editor: "textfield"
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
    },
    filters: [
        {
            title: "By Parent",
            name: "adm_division",
            ftype: "lookup",
            lookup: "gis.division"
        }
    ],
    //
    onPrimaryAddressChange: function(checkbox, newValue, oldValue, eOpts) {
        var me = this,
            grid = checkbox.column.up("gridpanel"),
            store = grid.getStore(),
            sLen = store.getCount();
        if(sLen === 1) {
            // Only one value
            if(!newValue) {
                // Restore primary address
                store.getAt(0).set("is_primary", true);
            }
        } else {
            if(!newValue) {
                // Resetting primary address
                checkbox.setValue(true);
            } else {
                // Resetting all other values
                var currentId = grid.getSelectionModel().getSelection()[0].get("id");
                store.each(function(r) {
                    if(r.get("id") !== currentId) {
                        r.set("is_primary", false);
                    }
                });
            }
        }
    },
    //
    onFillEntrances: function() {
        var me = this;
        Ext.create("NOC.gis.building.FillEntrancesForm", {app: me});
    },
    //
    fillEntrances: function(cfg) {
        var me = this,
            entrance = parseInt(cfg.first_entrance),
            firstHome = parseInt(cfg.first_home),
            nEntrances = parseInt(cfg.n_entrances),
            firstFloor = cfg.first_floor,
            lastFloor = cfg.last_floor,
            homesPerEntrance = parseInt(cfg.homes_per_entrance),
            result = me.currentRecord.get("entrances") || [],
            i;
        for(i = 0; i < nEntrances; i++) {
            result.push({
                number: String(entrance),
                first_floor: firstFloor,
                last_floor: lastFloor,
                first_home: String(firstHome),
                last_home: String(firstHome + homesPerEntrance - 1)
            });
            entrance += 1;
            firstHome += homesPerEntrance;

        }
        me.currentRecord.set("entrances", result);
        me.form.setValues({entrances: result});
        // Update floors
        if(!parseInt(me.form.getValues().floors)) {
            me.form.setValues({floors: lastFloor});
        }
        // Update homes
        if(!parseInt(me.form.getValues().homes)) {
            var homes = 0;
            for(i = 0; i < result.length; i++) {
                var r = result[i],
                    f = parseInt(r.first_home),
                    l = parseInt(r.last_home);
                if(f && l && f <= l) {
                    homes += l - f + 1;
                }
            }
            if(homes) {
                me.form.setValues({homes: String(homes)});
            }
        }
    }
});
