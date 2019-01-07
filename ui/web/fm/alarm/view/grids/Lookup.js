//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Lookup");

Ext.define("NOC.fm.alarm.view.grids.Lookup", {
    extend: "Ext.form.field.ComboBox",
    alias: "widget.fm.alarm.lookup",
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
    stateful: false,
    autoSelect: false,
    pageSize: true,
    labelAlign: "top",
    width: "100%",
    store: {
        fields: ["id", "label"],
        pageSize: 25,
        // remoteSort: true,
        // sorters: [
        //     {
        //         property: "label"
        //     }
        // ],
        // sorters: "label",
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
    triggers: {
        clear: {
            cls: "x-form-clear-trigger",
            hidden: true,
            weight: -1,
            handler: function(field) {
                field.setValue(null);
                field.fireEvent("select", field);
            }
        }
    },
    listeners: {
        change: function(field, value) {
            if(value == null || value === "") {
                this.getTrigger("clear").hide();
                return;
            }
            this.getTrigger("clear").show();
        }
    },
    initComponent: function() {
        this.store.proxy.url = this.url;
        // Fix combobox with remote paging
        this.pickerId = this.getId() + '-picker';
        this.callParent();
    }
});