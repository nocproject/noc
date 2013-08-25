//---------------------------------------------------------------------
// fm.mib application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mib.Application");

Ext.define("NOC.fm.mib.Application", {
    extend: "NOC.core.ModelApplication",
    model: "NOC.fm.mib.Model",
    search: true,

    columns: [
        {
            text: "MIB",
            dataIndex: "name",
            flex: 1
        },
        {
            text: "Last Updated",
            dataIndex: "last_updated",
            width: 100
        }
    ],

    createForm: function() {
        var me = this;
        //
        me.treeStore = Ext.create("Ext.data.TreeStore", {
            root: {
                expanded: false,
                children: []
            }
        });
        //
        return {
            xtype: "treepanel",
            store: me.treeStore,
            rootVisible: true
        }
    }
});
