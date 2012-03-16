//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "NOC.core.Application",
    requires: ["NOC.core.ModelStore"],
    layout: "fit",
    search: false,
    filters: null,
    toolbar: [],  // Additional toolbar buttons

    initComponent: function() {
        var me = this;
        // Permissions
        me.can_read = false;
        me.can_create = false;
        me.can_update = false;
        me.can_delete = false;
        // set base_url
        var n = this.self.getName().split("."),
            app_name = n[1] + "." + n[2];
        me.base_url = "/" + n[1] + "/" + n[2] + "/";
        // Variables
        me.current_query = {};
        // Create store
        var store = Ext.create("NOC.core.ModelStore", {
            model: me.model,
            autoLoad: true,
            pageSize: 1,  // Increased by AutoSize plugin
            remoteSort: true,
            remoteFilter: true
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
        // Setup Grid toolbar
        var grid_toolbar = [];
        if (me.search) {
            grid_toolbar = grid_toolbar.concat([
                {
                    xtype: "textfield",
                    name: "search_field",
                    itemId: "search_field",
                    emptyText: "Search...",
                    inputType: "search",
                    hideLabel: true,
                    width: 200,
                    listeners: {
                        change: {
                            fn: me.on_search,
                            scope: me,
                            buffer: 200
                        }
                    }
                }
            ]);
        }
        grid_toolbar = grid_toolbar.concat([
            {
                itemId: "create",
                text: "Add",
                iconCls: "icon_add",
                tooltip: "Add new record",
                disabled: true,
                scope: me,
                handler: function() {
                    this.new_record();
                }
            }
        ], me.toolbar);
        // Initialize panels
        // Filters
        var grid_rbar = null;
        me.filter_getters = [];
        if(me.filters) {
            var fh = Ext.bind(me.on_filter, me);
            grid_rbar = {
                xtype: "panel",
                width: 208,
                title: "Filter",
                padding: 4,
                items: me.filters.map(function(f) {
                    var ft = {
                        boolean: "NOC.core.modelfilter.Boolean",
                        lookup: "NOC.core.modelfilter.Lookup",
                        vcfilter: "NOC.core.modelfilter.VCFilter",
                        afi: "NOC.core.modelfilter.AFI",
                        vc: "NOC.core.modelfilter.VC",
                        tag: "NOC.core.modelfilter.Tag"
                    }[f.ftype];
                    var fc = Ext.Object.merge(f, {
                        referrer: app_name
                    });
                    var fg = Ext.create(ft, fc);
                    fg.handler = fh;
                    me.filter_getters = me.filter_getters.concat(
                        Ext.bind(fg.getFilter, fg)
                    );
                    return fg;
                })
            };
        }
        // Grid
        var grid_panel = {
            xtype: 'gridpanel',
            store: store,
            columns: this.columns,
            border: false,
            autoScroll: true,
            plugins: [Ext.create("Ext.ux.grid.AutoSize")],
            dockedItems: [
                {
                    xtype: "toolbar",
                    items: grid_toolbar
                },
                {
                    xtype: "pagingtoolbar",
                    store: store,
                    dock: "bottom",
                    displayInfo: true
                }
            ],
            rbar: grid_rbar,
            listeners: {
                select: function(view, record) {
                    var app = this.up("panel");
                    // Check permissions
                    if (!app.can_read && !app.can_update)
                        return;
                    app.edit_record(record);
                }
            }
        };
        // Form
        var form_panel = {
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
                    }].concat(me.fields),
                buttonAlign: "left",
                buttons: [
                    {
                        itemId: "save",
                        text: "Save",
                        iconCls: "icon_accept",
                        formBind: true,
                        disabled: true,
                        scope: this,
                        handler: function() {
                            if(!this.form.isValid())
                                return;
                            var v = this.form.getFieldValues();
                            // Fetch comboboxes labels
                            this.form.getFields().each(function(field) {
                                if(Ext.isDefined(field.getLookupData))
                                    v[field.name + "__label"] = field.getLookupData();
                            });
                            this.save_record(v);
                        }
                    },
                    {
                        itemId: "reset",
                        text: "Reset",
                        iconCls: "icon_cancel",
                        disabled: true,
                        scope: me,
                        handler: function() {
                            this.form.reset();
                        }
                    },
                    {
                        itemId: "close",
                        text: "Close",
                        iconCls: "icon_arrow_up",
                        scope: me,
                        handler: function() {
                            this.toggle();
                        }
                    },
                    {
                        itemId: "delete",
                        text: "Delete",
                        iconCls: "icon_delete",
                        disabled: true,
                        scope: me,
                        handler: function() {
                            Ext.Msg.show({
                                title: "Delete record?",
                                msg: "Do you wish to delete record? This operation cannot be undone!",
                                buttons: Ext.Msg.YESNO,
                                icon: Ext.window.MessageBox.QUESTION,
                                modal: true,
                                fn: Ext.bind(function(button) {
                                    if (button == "yes")
                                        this.delete_record();
                                }, this)
                            });
                        }
                    }
                ]
            }
        };

        Ext.apply(me, {
            items: [grid_panel, form_panel]
        });

        // Initialize component
        me.callParent(arguments);
        // Create shortcuts
        var grid = me.items.items[0],
            form = me.down("form"),
            grid_toolbar = grid.dockedItems.items[1],
            form_toolbar = form.dockedItems.first();
        me.create_button = grid_toolbar.getComponent("create");
        me.save_button = form_toolbar.getComponent("save");
        me.reset_button = form_toolbar.getComponent("reset");
        me.delete_button = form_toolbar.getComponent("delete");
        // Request permissions
        Ext.Ajax.request({
            method: "GET",
            url: this.base_url + "permissions/",
            scope: me,
            success: function(response) {
                var permissions = Ext.decode(response.responseText);
                this.set_permissions(permissions);
            }});
    },
    // Add shortcuts references
    afterRender: function() {
        var me = this;
        me.callParent(arguments);
        me.grid = me.down("gridpanel");
        me.store = me.grid.store;
        me.form = me.down("form").getForm();
        me.grid_toolbar = me.grid.dockedItems.items[1];

        //var gridpanel = this.items.items[0];
        if(me.search) {
            me.search_field = me.grid_toolbar.getComponent("search_field");
        }
    },
    // Toggle Grid/Form
    toggle: function() {
        // swap items. Because 'fit' layout accept only 1 item
        var me = this,
            tmp = me.items.items[0];
        me.items.items[0] = this.items.items[1];
        me.items.items[1] = tmp;

        me.doLayout();
        me.doComponentLayout();
    },
    // Save changed data
    save_record: function(data) {
        var mv = Ext.create(this.model, data).validate();

        if(!mv.isValid()) {
            // @todo: Error report
            return;
        }
        if (data["id"]) {
            // Change
            var record = this.grid.getSelectionModel().getLastSelected();
            record.set(data);
            this.store.sync();
        } else {
            // Create
            this.store.insert(0, [data]);
            this.store.sync();
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
    new_record: function(defaults) {
        var me = this;
        me.form.reset();
        if(defaults) {
            me.form.setValues(defaults);
        }
        console.log(me.title);
        me.toggle();
        me.form.getFields().first().focus(false, 100);
        // Activate delete button
        me.delete_button.setDisabled(true);
        me.save_button.setDisabled(!this.can_create);
        me.reset_button.setDisabled(!this.can_create);
    },
    // Edit record. Hide grid and open form
    edit_record: function(record) {
        // Show edit form
        this.toggle();
        // Load records
        this.form.loadRecord(record);
        // Focus on first field
        this.form.getFields().first().focus(false, 100);
        // Activate delete button
        this.delete_button.setDisabled(!this.can_delete);
        this.save_button.setDisabled(!this.can_update);
        this.reset_button.setDisabled(!this.can_update);
    },
    // Delete record
    delete_record: function() {
        var record = this.grid.getSelectionModel().getLastSelected();
        this.store.remove(record);
        this.store.sync();
        this.toggle();
    },
    // Reload store with current query
    refresh_store: function() {
        var me = this;
        if(me.current_query)
            me.store.setExtraParams(me.current_query);
        me.store.load();
    },
    // Search
    on_search: function() {
        var me = this,
            v = me.search_field.getValue();
        if(v)
            me.current_query["__query"] = v;
        else
            delete me.current_query["__query"];
        me.refresh_store();
    },
    // Filter
    on_filter: function() {
        var me = this,
            fexp = {};
        Ext.each(me.filter_getters, function(g) {
            fexp = Ext.Object.merge(fexp, g());
        });
        if(me.current_query["__query"])
            fexp["__query"] = me.current_query["__query"];
        me.current_query = fexp;
        me.refresh_store();
    }
});
