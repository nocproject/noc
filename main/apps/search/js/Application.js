//---------------------------------------------------------------------
// main.search application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.search.Application");

Ext.define("NOC.main.search.Application", {
    extend: "NOC.core.Application",
    initComponent: function() {
        var me = this;
        me.store = Ext.create("NOC.main.search.SearchStore");
        me.searchField = Ext.create("Ext.ux.form.SearchField", {
            fieldLabel: "Search",
            labelWidth: 40,
            width: "500",
            scope: me,
            handler: me.doSearch
        });
        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            columns: [
                {
                    text: "Result",
                    xtype: "templatecolumn",
                    flex: 1,
                    tpl: "<b>{title}</b><br/>{card}<tpl if='tags'>Tags: {tags}</tpl>"
                }
            ],
            listeners: {
                scope: me,
                select: me.onSelect
            }
        });
        Ext.apply(me, {
            items: [
                me.grid
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.searchField
                    ]
                }
            ]
        });
        me.callParent();
        // Process commands
        if(me.noc.cmd) {
            switch(me.noc.cmd.cmd) {
                case "search":
                    me.searchField.setValue(me.noc.cmd.query);
                    break;
            }
        }

    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        me.searchField.focus();
        var v = me.searchField.getValue();
        if(v !== "") {
            me.doSearch(v);
        }
    },
    //
    doSearch: function(query) {
        var me = this;
        Ext.Ajax.request({
            url: "/main/search/",
            method: "POST",
            jsonData: {
                query: query
            },
            scope: me,
            success: function(response) {
                me.showResult(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to search");
            }
        });
    },
    //
    showResult: function(result) {
        var me = this;
        me.searchField.focus();
        me.store.loadData(result);
    },
    //
    onSelect: function(model, record, index, opts) {
        var me = this,
            i = record.get("info");
        NOC.launch(i[0], i[1], i[2]);
    }
});
