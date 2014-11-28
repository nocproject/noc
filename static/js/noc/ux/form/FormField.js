//---------------------------------------------------------------------
// Ext.ux.form.FormField
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining Ext.ux.form.FormField");

Ext.define("Ext.ux.form.FormField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    alias: "widget.formfield",
    border: false,
    form: [],

    initComponent: function() {
        var me = this;

        me.formPanel = Ext.create("Ext.form.Panel", {
            items: me.form,
            border: false
        });

        Ext.apply(me, {
            items: [me.formPanel]
        });
        me.callParent();
    },
    //
    getValue: function() {
        var me = this;
        return me.formPanel.getForm().getValues();
    },
    //
    setValue: function(value) {
        var me = this;
        me.formPanel.getForm().setValues(value);
    }
});
