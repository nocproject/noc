//---------------------------------------------------------------------
// gis.building FillEntrancesForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.building.FillEntrancesForm");

Ext.define("NOC.gis.building.FillEntrancesForm", {
    extend: "Ext.window.Window",
    modal: true,
    autoShow: true,
    width: 270,
    height: 260,
    title: "Fill Entrances",
    app: null,

    initComponent: function() {
        var me = this;

        me.form = Ext.create("Ext.form.Panel", {
            items: [
                {
                    name: "first_entrance",
                    xtype: "numberfield",
                    fieldLabel: "First Entrance",
                    minValue: 1,
                    value: 1,
                    allowBlank: false
                },
                {
                    name: "first_home",
                    xtype: "numberfield",
                    fieldLabel: "First Home",
                    minValue: 1,
                    value: 1,
                    allowBlank: false
                },
                {
                    name: "n_entrances",
                    xtype: "numberfield",
                    fieldLabel: "Entrances",
                    minValue: 1,
                    value: 1,
                    allowBlank: false,
                    listeners: {
                        scope: me,
                        change: me.onChange
                    }
                },
                {
                    name: "first_floor",
                    xtype: "numberfield",
                    fieldLabel: "First Floor",
                    minValue: 1,
                    value: 1,
                    allowBlank: false
                },
                {
                    name: "last_floor",
                    xtype: "numberfield",
                    fieldLabel: "Last Floor",
                    minValue: 1,
                    value: 1,
                    allowBlank: false
                },
                {
                    name: "homes_per_entrance",
                    xtype: "numberfield",
                    fieldLabel: "Homes per Entrance",
                    value: 1,
                    minValue: 1,
                    allowBlank: false,
                    listeners: {
                        scope: me,
                        change: me.onChange
                    }
                },
                {
                    name: "new_homes",
                    xtype: "displayfield",
                    fieldLabel: "New Homes",
                    value: "1"
                }
            ],
            buttons: [
                {
                    text: "Create",
                    glyph: NOC.glyph.plus,
                    disabled: true,
                    formBind: true,
                    scope: me,
                    handler: me.onCreateEntrances
                }
            ]
        });
        Ext.apply(me, {
            items: [me.form]
        });
        me.callParent();
    },
    //
    onCreateEntrances: function() {
        var me = this,
            data = me.form.getForm().getValues();
        me.app.fillEntrances(data);
        me.close();
    },
    // Calculate new homes
    onChange: function() {
        var me = this,
            data = me.form.getForm().getValues(),
            nEntrances = parseInt(data.n_entrances),
            homesPerEntrance = parseInt(data.homes_per_entrance);
        if(nEntrances && homesPerEntrance) {
            me.form.getForm().setValues({
                new_homes: nEntrances * homesPerEntrance
            });
        }
    }
});
