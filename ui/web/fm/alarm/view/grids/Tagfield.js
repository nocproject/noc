//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Tagfield");

Ext.define("NOC.fm.alarm.view.grids.Tagfield", {
    extend: "Ext.form.field.Tag",
    alias: "widget.fm.alarm.tagfield",
    controller: "fm.alarm.tagfield",
    requires: [
        "NOC.fm.alarm.view.grids.TagfieldController"
    ],
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    minChars: 2,
    pageSize: true,
    store: {
        fields: ["id", "label"],
        pageSize: 25,
        proxy: {
            type: "rest",
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
    },
    config: {
        selected: null
    },
    twoWayBindable: [
        "selected"
    ],
    listeners: {
        change: "onChange"
    },
    initComponent: function() {
        this.store.proxy.url = this.url;
        this.callParent();
    },
    setSelected: function(value, skip) {
        this.callParent([value]);
        if(!skip) {
            this.setWidgetValues(value);
        }
    },
    setWidgetValues: function(data) {
        this.setSelection(data);
    }
});
