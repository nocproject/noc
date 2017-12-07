//---------------------------------------------------------------------
// NOC.core.LookupField -
// Lookup form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.LookupField");

Ext.define("NOC.core.LookupField", {
    extend: "Ext.form.ComboBox",
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    forceSelection: false,
    minChars: 2,
    typeAhead: true,
    triggerAction: "all",
    query: {},
    stateful: false,
    autoSelect: false,
    pageSize: true,
    listConfig: {
        minWidth: 240
    },
    isLookupField: true,
    restUrl: null,

    initComponent: function() {
        var me = this;

        // Calculate restUrl
        if(!me.restUrl
            && Ext.String.startsWith(me.$className, 'NOC.')
            && Ext.String.endsWith(me.$className, 'LookupField')) {
            me.restUrl = me.$className.replace('NOC', '').replace(/\./g, '/').replace('/LookupField', '/lookup/');
        }

        if(!me.restUrl) {
            throw "Cannot determine restUrl for " + me.$className;
        }

        Ext.apply(me, {
            store: {
                fields: ["id", "label"],
                pageSize: 25,
                proxy: {
                    type: "rest",
                    url: me.restUrl,
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    extraParams: {
                        "__format": "ext"
                    },
                    reader: {
                        type: "json",
                        rootProperty: "data",
                        totalProperty: "total",
                        successProperty: "success"
                    }
                }
            }
        });
        if(me.query) {
            Ext.apply(me.store.proxy.extraParams, me.query);
        }
        // Fix combobox with remote paging
        me.pickerId = me.getId() + '_picker';
        // end
        me.callParent();
        me.on("specialkey", me.onSpecialKey, me, {delay: 100});
        me.on('change', function(element, newValue) {
            if(newValue === null) {
                me.clearValue();
                me.fireEvent('clear');
            }
        });
    },

    getLookupData: function() {
        return this.getDisplayValue();
    },

    onSpecialKey: function(field, e) {
        var me = this;
        switch(e.keyCode) {
            case e.ESC:
                me.clearValue();
                me.fireEvent("clear");
                break;
        }
    },

    onBeforeQuery: function() {
        var me = this,
            v = this.getRawValue();
        if (typeof v === "undefined" || v === null || v === "") {
            me.clearValue();
            me.fireEvent("clear");
        }
    },

    setValue: function(value, doSelect) {
        var me = this,
            vm,
            params = {};
        if(typeof value === "string" || typeof value === "number") {
            if(value === "" || value === 0) {
                me.clearValue();
                return;
            }
            params[me.valueField] = value;
            Ext.Ajax.request({
                url: me.restUrl,
                method: "GET",
                scope: me,
                params: params,
                success: function (response) {
                    var data = Ext.decode(response.responseText);
                    if (data.length === 1) {
                        vm = me.store.getModel().create(data[0]);
                        me.setValue(vm);
                        if(doSelect) {
                            me.fireEvent("select", me, vm, {});
                        }
                    }
                }
            });
        } else {
            me.callParent([value]);
        }
    },

    // Called by ModelApplication
    cleanValue: function(record, restURL) {
        var me = this,
            rv = record.get(me.name),
            mv = {};
        if(!rv || rv === "" || rv === 0) {
            return ""
        }
        mv[me.valueField] = rv;
        mv[me.displayField] = record.get(me.name + "__label");
        return me.store.getModel().create(mv)
    }
});
