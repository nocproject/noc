//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "NOC.core.Application",
    layout: "anchor",
    
    initComponent: function() {
        // Permissions
        this.can_read = false;
        this.can_create = false;
        this.can_update = false;
        this.can_delete = false;
        // set base_url
        var n = this.self.getName().split(".");
        this.base_url = "/" + n[1] + "/" + n[2] + "/";
        // Create store
        var store = Ext.create("Ext.data.Store", {
            model: this.model,
            autoLoad: true,
            pageSize: 10
        });
        // Setup REST proxy
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
                                    id: "create",
                                    text: "Add",
                                    tooltip: "Add new record",
                                    disabled: true,
                                    handler: function() {
                                        var app = this.up("panel").up("panel");
                                        app.new_record();
                                    }
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
                            var app = this.up("panel");
                            // Check permissions
                            if (!app.can_read && !app.can_update)
                                return;
                            app.edit_record(record);
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
                            id: "save",
                            text: "Save",
                            formBind: true,
                            disabled: true,
                            handler: function() {
                                var form = this.up("panel").getForm();
                                if(!form.isValid())
                                    return;
                                var v = form.getValues(),
                                    app = this.up("panel").up("panel");
                                app.save_record(v);
                            }
                        },
                        {
                            id: "reset",
                            text: "Reset",
                            disabled: true,
                            handler: function() {
                                this.up("panel").getForm().reset();
                            }
                        },
                        {
                            id: "close",
                            text: "Close",
                            handler: function() {
                                var app = this.up("panel").up("panel");
                                app.toggle();
                            }
                        },
                        {
                            id: "delete",
                            text: "Delete",
                            disabled: true,
                            handler: function() {
                                var app = this.up("panel").up("panel");
                                Ext.Msg.show({
                                    title: "Delete record?",
                                    msg: "Do you wish to delete record? This operation cannot be undone!",
                                    buttons: Ext.Msg.YESNO,
                                    icon: Ext.window.MessageBox.QUESTION,
                                    modal: true,
                                    fn: function(button) {
                                        if (button == "yes")
                                            app.delete_record();
                                    }
                                });
                            }
                        }
                    ]
                })
            ]
        });
        // Initialize component
        this.callParent(arguments);
        // Create shortcuts
        var grid = this.items.items[0],
            form = this.items.items[1],
            grid_toolbar = grid.dockedItems.items[1],
            form_toolbar = form.dockedItems.first();
        this.create_button = grid_toolbar.getComponent("create");
        this.save_button = form_toolbar.getComponent("save");
        this.reset_button = form_toolbar.getComponent("reset");
        this.delete_button = form_toolbar.getComponent("delete");
        // Request permissions
        Ext.Ajax.request({
            method: "GET",
            url: this.base_url + "permissions/",
            scope: this,
            success: function(response) {
                var permissions = Ext.decode(response.responseText);
                this.set_permissions(permissions);
            }});
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
        var mv = Ext.create(this.model, data).validate();
        
        if(!mv.isValid()) {
            // @todo: Error report
            return;
        }
        if (data["id"]) {
            // Change
            var record = grid.getSelectionModel().getLastSelected();
            record.set(data);
            store.sync();
        } else {
            // Create
            store.insert(0, [data]);
            store.sync();
        }
        this.toggle();
    },
    // Set application permissions
    set_permissions: function(permissions) {
        // Set read permission
        this.can_read = permissions.indexOf("read") >= 0;
        // Set create permission
        this.can_create = permissions.indexOf("create") >= 0;
        this.create_button.setDisabled(!this.can_create);
        // Set update permission
        this.can_update = permissions.indexOf("update") >= 0;
        // Set delete permission
        this.can_delete = permissions.indexOf("delete") >= 0;
    },
    // New record. Hide grid and open form
    new_record: function() {
        var form = this.items.items[1].getForm();
        form.reset();
        this.toggle();
        form.getFields().first().focus(false, 100);
        // Activate delete button
        this.delete_button.setDisabled(true);
        this.save_button.setDisabled(!this.can_create);
        this.reset_button.setDisabled(!this.can_create);
    },
    // Edit record. Hide grid and open form
    edit_record: function(record) {
        // Show edit form
        var form = this.items.items[1].getForm();
        this.toggle();
        // Load records
        form.loadRecord(record);
        // Focus on first field
        form.getFields().first().focus(false, 100);
        // Activate delete button
        this.delete_button.setDisabled(!this.can_delete);
        this.save_button.setDisabled(!this.can_update);
        this.reset_button.setDisabled(!this.can_update);
    },
    // Delete record
    delete_record: function() {
        var grid = this.items.items[0],
            store = grid.store,
            record = grid.getSelectionModel().getLastSelected();
        store.remove(record);
        store.sync();
        this.toggle();        
    }
});
