//---------------------------------------------------------------------
// inv.inv AddGroupForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.map.AddObjectForm");

Ext.define("NOC.inv.inv.plugins.map.AddObjectForm", {
    extend: "Ext.window.Window",
    requires: [],
    modal: true,
    autoShow: true,
    closeable: true,
    objectModelId: null,
    objectModelName: null,
    newPosition: null,
    positionSRID: null,
    app: null,
    width: 400,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.form = Ext.create("Ext.form.Panel", {
            bodyPadding: 4,
            layout: "anchor",
            defaults: {
                anchor: "100%",
                labelWidth: 40
            },
            items: [
                {
                    xtype: "displayfield",
                    name: "display_position"
                },
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: "Name",
                    allowBlank: false
                }
            ],
            buttons: [
                {
                    text: "Close",
                    scope: me,
                    handler: me.onPressClose
                },
                {
                    text: "Add",
                    glyph: NOC.glyph.plus,
                    scope: me,
                    handler: me.onPressAdd,
                    formBind: true
                }
            ]
        });

        Ext.apply(me, {
            title: "Create new " + me.objectModelName,
            items: [me.form]
        });
        me.callParent();
        me.form.getForm().setValues({
            objectmodel: "Zhopa",
            display_position: me.newPosition.toString()
        });
    },
    //
    onPressClose: function() {
        var me = this;
        me.close();
    },
    onPressAdd: function() {
        var me = this,
            values = me.form.getValues();
        console.log(values);
        Ext.Ajax.request({
            url: "/inv/inv/plugin/map/",
            method: "POST",
            jsonData: {
                model: me.objectModelId,
                name: values.name,
                srid: me.positionSRID,
                x: me.newPosition.lon,
                y: me.newPosition.lat
            },
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.close();
                me.app.app.showObject(data.id, true);
            },
            failure: function() {
                NOC.error("Failed to save");
            }
        });
    }
});
