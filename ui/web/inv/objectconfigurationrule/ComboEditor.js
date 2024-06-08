//---------------------------------------------------------------------
// inv.objectconfigurationrule.comboEditor widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectconfigurationrule.ComboEditor");

Ext.define("NOC.inv.objectconfigurationrule.ComboEditor", {
    extend: "Ext.form.field.ComboBox",
    alias: "widget.inv.objectconfigurationrule.comboEditor",
    displayField: "label",
    valueField: "id",
    editable: true,
    forceSelection: true,
    multiSelect: true,
    autoLoadOnValue: true,
    queryMode: "remote",
    queryParam: "__query",
    triggers: {
        clear: {
            cls: 'x-form-clear-trigger',
            weight: -1,
            handler: function(field) {
                field.setValue(null);
            }
        },
    },
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            store: {
                fields: ["id", "label"],
                pageSize: 0,
                proxy: {
                    type: "rest",
                    url: me.url,
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    reader: {
                        type: "json",
                        rootProperty: "data",
                        totalProperty: "total",
                        successProperty: "success"
                    }
                }
            }
        });
        this.callParent();
    },
    setValue: function(value) {
        if(Ext.isArray(value)) {
            value = Ext.Array.map(value, function(item) {
                if(Ext.isObject(item)) {
                    return item.id;
                }
                return item;
            });
        }
        this.callParent([value]);
    }
});
