//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "Ext.panel.Panel",
    
    initComponent: function() {
        // Create store
        var store = Ext.create("Ext.data.Store", {
            model: this.model,
            autoLoad: true,
            autoSync: true,
            pageSize: 10
        });
        // Initialize panels
        Ext.apply(this, {
            items: [
                // Grid
                Ext.create("Ext.grid.Panel", {
                    store: store,
                    columns: this.columns,
                    collapsible: true,
                    animCollapse: true,
                    collapseMode: "mini",
                    split: true,
                    preventHeader: true,
                    border: false,
                    dockedItems: [
                        {
                            xtype: "toolbar",
                            items: [
                                {
                                    text: "Add",
                                    tooltip: "Add new record",
                                    disabled: true
                                },
                                {
                                    text: "Remove",
                                    tooltip: "Remove selected record",
                                    disabled: true
                                }
                            ]
                        },
                        {
                            xtype: "pagingtoolbar",
                            store: store,
                            dock: "bottom",
                            displayInfo: true
                        }
                    ]
                }),
                // Form
                Ext.create("Ext.form.Panel", {
                    items: this.fields,
                    buttons: [
                        {
                            text: "Save"
                        }
                    ]
                })
            ]
        });
        this.callParent(arguments);
    }
});
