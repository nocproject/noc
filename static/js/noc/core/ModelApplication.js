//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "Ext.panel.Panel",
    layout: "anchor",
    
    initComponent: function() {
        // Create store
        var store = Ext.create("Ext.data.Store", {
            model: this.model,
            autoLoad: true,
            pageSize: 10
        });
        store.setProxy(Ext.create("Ext.data.RestProxy", {
            url: store.model.prototype.rest_url,
            pageParam: "__page",
            startParam: "__start",
            limitParam: "__limit",
            sortParam: "__sort",
            extraParams: {
                "__format": "ext"
            },
            reader: {
                type: "json",
                root: "data",
                totalProperty: "total",
                successProperty: "success"
            },
            writer: {
                type: "json"
            }    
        }));
        // Initialize panels
        Ext.apply(this, {
            items: [
                // Grid
                Ext.create("Ext.grid.Panel", {
                    store: store,
                    columns: this.columns,
                    border: false,
                    hidden: false,
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
                    ],
                    listeners: {
                        itemclick: function(view, record) {
                            var form = this.up("panel").items.items[1].getForm();
                            this.up("panel").toggle();
                            // Load records
                            form.loadRecord(record);
                            // Focus on first field
                            form.getFields().first().focus(false, 100);
                        }
                    }
                }),
                // Form
                Ext.create("Ext.form.Panel", {
                    border: true,
                    hidden: true,
                    padding: 4,
                    items: [
                        {
                            xtype: "container",
                            html: "Change",
                            padding: 4,
                            style: {
                                fontWeight: "bold"
                            }
                        },
                        {
                            xtype: "hiddenfield",
                            name: "id"
                        }].concat(this.fields),
                    buttons: [
                        {
                            text: "Save",
                            formBind: true,
                            handler: function() {
                                var form = this.up("panel").getForm();
                                if(!form.isValid())
                                    return;
                                var v = form.getValues();
                                this.up("panel").up("panel").save_record(v);
                            }
                        },
                        {
                            text: "Reset",
                            handler: function() {
                                this.up("panel").getForm().reset();
                            }
                        },
                        {
                            text: "Close",
                            handler: function() {
                                this.up("panel").up("panel").toggle();
                            }
                        }
                    ]
                })
            ]
        });
        this.callParent(arguments);
    },
    // Toggle Grid/Form
    toggle: function() {
        var toggle_panel = function(panel) {
            if (panel.hidden) {
               panel.show();
            } else
               panel.hide();
        }
        toggle_panel(this.items.items[0]);
        toggle_panel(this.items.items[1]);
    },
    // Save changed data
    save_record: function(data) {
        var grid = this.items.items[0],
            store = grid.store;
        
        if (data["id"]) {
            // Change
            var record = grid.getSelectionModel().getLastSelected();
            record.set(data);
            store.sync();
        } else {
            // Create
        }
        this.toggle();
    }
});
