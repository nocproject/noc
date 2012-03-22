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
        var sclass = this.__proto__.$className.replace("LookupField", "Lookup");
        Ext.applyIf(this, {
            store: Ext.create(sclass)
        });
        if(this.query) {
            Ext.apply(this.store.proxy.extraParams, this.query);
        }
        this.callParent();
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
                    this,
                    {single: true}
                );
                me.store.load({
                    params: {
                        id: value
                    }
                });
            }
        }
        return this.callParent([value]);
    },
    getLookupData: function() {
        return this.getDisplayValue();
    }
});
