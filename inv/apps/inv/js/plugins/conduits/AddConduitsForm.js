//---------------------------------------------------------------------
// inv.inv Add conduit form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.conduits.AddConduitsForm");

Ext.define("NOC.inv.inv.plugins.conduits.AddConduitsForm", {
    extend: "Ext.Window",
    title: "Add Conduits",
    closable: true,
    layout: "fit",
    app: null,
    modal: true,
    width: 400,
    height: 130,
    storeData: null,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            model: null,
            fields: ["id", "label", "name", "s_bearing", "map_distance"],
            data: me.storeData
        });

        me.targetCombo = Ext.create("Ext.form.field.ComboBox", {
            name: "connect_to",
            fieldLabel: "Connect to",
            allowBlank: false,
            store: me.store,
            displayField: "label",
            valueField: "id",
            anchor: "100%"
        });

        me.distanceField = Ext.create("Ext.form.field.Text", {
            name: "project_distance",
            fieldLabel: "Project distance (m)",
            allowBlank: true
        });

        me.formPanel = Ext.create("Ext.form.Panel", {
            items: [
                me.targetCombo,
                me.distanceField
            ],
            buttons: [
                {
                    text: "Connect",
                    glyph: NOC.glyph.plus,
                    formBind: true,
                    scope: me,
                    handler: me.onConnect
                },
                {
                    text: "Close",
                    glyph: NOC.glyph.times,
                    scope: me,
                    handler: me.onClose
                }
            ]
        });

        Ext.apply(me, {
            items: [me.formPanel]
        });

        me.callParent();
    },
    //
    onClose: function() {
        var me = this;
        me.close();
    },
    //
    onConnect: function() {
        var me = this,
            t = me.targetCombo.getValue(),
            r = me.targetCombo.findRecordByValue(t);
        me.app.addConduits({
            target_id: r.get("id"),
            target_name: r.get("name"),
            project_distance: parseFloat(me.distanceField.getValue()),
            s_bearing: r.get("s_bearing"),
            map_distance: r.get("map_distance")
        });
        me.close();
    }
});
