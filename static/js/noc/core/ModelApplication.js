//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "NOC.core.Application",
    layout: "fit",

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
                {
                    xtype: 'gridpanel',
                    store: store,
                    columns: this.columns,
                    border: false,
                    autoScroll: true,
                    plugins : [ Ext.create('Ext.ux.grid.AutoSize') ],
                    dockedItems: [
                        {
                            xtype: "toolbar",
                            items: [
                                {
                                    itemId: "create",
                                    text: "Add",
                                    iconCls: "icon_add",
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
                    },
                },
                // Form
                {
                    xtype: 'container',
                    layout: 'anchor',
                    items: {
                        xtype: 'form',
                        border: true,
                        padding: 4,
                        bodyPadding: 4,
                        defaults: {
                            enableKeyEvents: true,
                            listeners: {
                                specialkey: function(field, key) {
                                    if (field.xtype != "textfield")
                                        return;
                                    var get_button = function(scope, name) {
                                        return scope.up("panel").dockedItems.items[0].getComponent(name);
                                    }
                                    switch(key.getKey()) {
                                        case Ext.EventObject.ENTER:
                                            var b = get_button(this, "save");
                                            key.stopEvent();
                                            b.handler.call(b);
                                            break;
                                        case Ext.EventObject.ESC:
                                            var b = get_button(this, "reset");
                                            key.stopEvent();
                                            b.handler.call(b);
                                    }
                                }
                            }
                        },
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
                        buttonAlign: "left",
                        buttons: [
                            {
                                itemId: "save",
                                text: "Save",
                                iconCls: "icon_accept",
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
                                itemId: "reset",
                                text: "Reset",
                                iconCls: "icon_cancel",
                                disabled: true,
                                handler: function() {
                                    this.up("panel").getForm().reset();
                                }
                            },
                            {
                                itemId: "close",
                                text: "Close",
                                iconCls: "icon_arrow_up",
                                handler: function() {
                                    var app = this.up("panel").up("panel");
                                    app.toggle();
                                }
                            },
                            {
                                itemId: "delete",
                                text: "Delete",
                                iconCls: "icon_delete",
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
                    }
                }
            ]
        });


        // Initialize component
        this.callParent(arguments);
        // Create shortcuts
        var grid = this.items.items[0],
            form = this.down('form'),
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
        // swap items. Because 'fit' layout accept only 1 item
        var tmp = this.items.items[0];
        this.items.items[0] = this.items.items[1];
        this.items.items[1] = tmp;

        this.doLayout();
        this.doComponentLayout();
    },
    // Save changed data
    save_record: function(data) {
        var grid = this.down('gridpanel'),
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
        var form = this.up('panel').down('form').getForm();
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
        var form = this.down('form').getForm();
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
        var grid = this.down('gridpanel'),
            store = grid.store,
            record = grid.getSelectionModel().getLastSelected();
        store.remove(record);
        store.sync();
        this.toggle();
    }
});
