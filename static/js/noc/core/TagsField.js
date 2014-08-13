//---------------------------------------------------------------------
// NOC.core.TagsField -
// Tags Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TagsField");

Ext.define("NOC.core.TagsField", {
    extend: "Ext.form.field.Tag",
    alias: ["widget.tagsfield"],
    forceSelection: false,
    displayField: "label",
    valueField: "label",
    queryMode: "local",
    queryParam: "__query",
    createNewOnEnter: true,
    createNewOnBlur: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            store: Ext.create("Ext.data.Store", {
                fields: ["id", "label"],
                proxy: {
                    type: "ajax",
                    url: "/main/tag/lookup/",
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
            })
        });
        me.callParent();
    },
    //
    // Convert array of strings to array of models
    //
    setValue: function(value) {
        var me = this,
            valueRecord, cls, i, len;
        if (Ext.isEmpty(value)) {
            value = null;
        }
        if (Ext.isString(value) && me.multiSelect) {
            value = value.split(me.delimiter);
        }
        value = Ext.Array.from(value, true);
        for (i = 0, len = value.length; i < len; i++) {
            record = value[i];
            if (!record || !record.isModel) {
                valueRecord = {};
                valueRecord[me.valueField] = record;
                valueRecord[me.displayField] = record;
                cls = me.valueStore.getModel();
                valueRecord = new cls(valueRecord);
                value[i] = valueRecord;
            }
        }
        me.callParent([value]);
    }
});