//---------------------------------------------------------------------
// NOC.core.LookupField -
// Lookup form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.LookupField");

Ext.define("NOC.core.LookupField", {
    extend: "Ext.form.ComboBox",
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    forceSelection: true,
    minChars: 2,
    typeAhead: true,
    editable: true,
    query: {},

    initComponent: function() {
        var me = this,
            sclass = me.__proto__.$className.replace("LookupField",
                                                     "Lookup");
        Ext.applyIf(me, {
            store: Ext.create(sclass)
        });
        if(me.query) {
            Ext.apply(me.store.proxy.extraParams, me.query);
        }
        me.addEvents("clear");
        me.callParent();
        // @todo: clear event
        me.on("specialkey", me.onSpecialKey, me);
        me.on("blur", me.onBlur, me);
    },

    setValue: function(value) {
        var me = this;

        if(Ext.isDefined(value)) {
            if(me.store.loading) {
                // do not set value until store is loaded
                return me;
            }
            if(!me.store.data.length && value) {
                // store not ready. load
                // @todo: check for loop
                me.store.on(
                    "load",
                    Ext.bind(me.setValue, me, arguments),
                    me,
                    {single: true}
                );
                me.store.load({
                    params: {
                        id: value
                    }
                });
            }
        }
        return me.callParent([value]);
    },

    getLookupData: function() {
        return this.getDisplayValue();
    },

    onSpecialKey: function(field, e) {
        var me = this;
        if(e.ESC) {
            me.clearValue();
            me.fireEvent("clear");
        }
    },

    onBlur: function(field, e) {
        var me = this;
        console.log("BLUR", field, me.getDisplayValue(), me.getRawValue());
        if(!me.getRawValue()) {
            console.log("CLEAR");
            me.clearValue();
            me.fireEvent("clear");
        }
    }
});
