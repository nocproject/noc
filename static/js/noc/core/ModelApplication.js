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
    gridToolbar: [],  // Additional grid toolbar buttons
    formToolbar: [],  // Additional form toolbar buttons
    currentRecord: null,
    appTitle: null,
    createTitle: "Create {0}",
    changeTitle: "Change {0}",
    rowClassField: undefined,

    initComponent: function() {
        var me = this;
        // set base_url
        var n = this.self.getName().split("."),
            app_name = n[1] + "." + n[2];
        me.base_url = "/" + n[1] + "/" + n[2] + "/";
        // Variables
        me.currentQuery = {};
        // Create store
        me.store = Ext.create("NOC.core.ModelStore", {
            model: me.model,
            autoLoad: true,
            pageSize: 1  // Increased by AutoSize plugin
        });
        // Setup Grid toolbar
        var gridToolbar = [
            {
                xtype: "textfield",
                name: "search_field",
                itemId: "search_field",
                emptyText: "Search...",
                inputType: "search",
                hideLabel: true,
                width: 200,
                hasAccess: function(app) { return app.search === true;},
                listeners: {
                    change: {
                        fn: me.onSearch,
                        scope: me,
                        buffer: 200
                    }
                }
            },
            {
                itemId: "create",
                text: "Add",
                iconCls: "icon_add",
                tooltip: "Add new record",
                hasAccess: NOC.hasPermission("create"),
                scope: me,
                handler: function() {me.onNewRecord();}
            }
        ].concat(me.gridToolbar);
        // Initialize panels
        // Filters
        var grid_rbar = null;
        me.filterGetters = [];
        if(me.filters) {
            var fh = Ext.bind(me.onFilter, me);
            grid_rbar = {
                xtype: "form",
                itemId: "filters",
                width: 208,
                title: "Filter",
                padding: 4,
                tools: [
                    {
                        type: "close",
                        tooltip: "Reset filters",
                        scope: me,
                        handler: me.onResetFilters
                    }
                ],
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
                    me.filterGetters = me.filterGetters.concat(
                        Ext.bind(fg.getFilter, fg)
                    );
                    return fg;
                })
            };
        }
        // Grid
        var grid_panel = {
            xtype: "gridpanel",
            itemId: "grid",
            store: me.store,
            columns: me.columns,
            border: false,
            autoScroll: true,
            plugins: [Ext.create("Ext.ux.grid.AutoSize")],
            dockedItems: [
                {
                    xtype: "toolbar",
                    items: me.applyPermissions(gridToolbar)
                },
                {
                    xtype: "pagingtoolbar",
                    store: me.store,
                    dock: "bottom",
                    displayInfo: true
                }
            ],
            rbar: grid_rbar,
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me)
            },
            listeners: {
                itemdblclick: me.onEditRecord,
                select: me.onEditRecord
            }
        };
        // Form
        var formToolbar = [
            {
                itemId: "save",
                text: "Save",
                iconCls: "icon_disk",
                formBind: true,
                disabled: true,
                scope: me,
                // @todo: check access
                handler: me.onSave
            },
            {
                itemId: "close",
                text: "Close",
                iconCls: "icon_arrow_undo",
                scope: me,
                handler: me.onClose
            },
            {
                xtype: "tbseparator"
            },
            {
               itemId: "reset",
               text: "Reset",
               iconCls: "icon_cancel",
               disabled: true,
               scope: me,
               handler: me.onReset
            },
            {
               itemId: "delete",
               text: "Delete",
               iconCls: "icon_delete",
               disabled: true,
               hasAccess: NOC.hasPermission("delete"),
               scope: me,
               handler: me.onDelete
            },
            {
                xtype: "tbseparator",
                itemId: "custom_sep"
            }
        ].concat(me.formToolbar);

        var form_panel = {
            xtype: 'container',
            itemId: "form",
            layout: "fit",
            items: {
                xtype: 'form',
                border: true,
                padding: 4,
                bodyPadding: 4,
                defaults: {
                    enableKeyEvents: true,
                    listeners: {
                        specialkey: {
                            scope: me,
                            fn: me.onFormSpecialKey
                        }
                    }
                },
                items: [
                    {
                        xtype: "container",

                        html: "Title",
                        itemId: "form_title",
                        padding: 4,
                        style: {
                            fontWeight: "bold"
                        }
                    },
                    {
                        xtype: "hiddenfield",
                        name: "id"
                    }].concat(me.fields),
                tbar: me.applyPermissions(formToolbar)
            }
        };

        Ext.apply(me, {
            items: [grid_panel, form_panel]
        });

        // Initialize component
        me.callParent(arguments);
        me.currentRecord = null;
        // Create shortcuts
        var grid = me.getComponent("grid"),
            form = me.getComponent("form").items.first(),
            gt = grid.dockedItems.items[1],
            ft = form.dockedItems.first();
        me.grid = grid;
        me.form = form.getForm();
        me.search_field = gt.getComponent("search_field");
        me.create_button = gt.getComponent("create");
        me.saveButton = ft.getComponent("save");
        me.closeButton = ft.getComponent("close");
        me.resetButton = ft.getComponent("reset");
        me.deleteButton = ft.getComponent("delete");
        me.formTitle = form.getComponent("form_title");
        if(me.filters) {
            me.filterPanel = me.grid.getComponent("filters");
        }
    },
    // Toggle Grid/Form
    toggle: function() {
        // swap items. Because 'fit' layout accept only 1 item
        var me = this;
        me.items.items = [me.items.last(), me.items.first()];
        // Apply changes to form toolbar
        if(me.items.first().itemId === "form") {
            // Switched to form
            // console.log("Switched to form");
        }
        // Layout
        me.doLayout();
        me.doComponentLayout();
    },
    // Save changed data
    saveRecord: function(data) {
        var me = this,
            mv = Ext.create(this.model, data).validate(),
            record;

        if(!mv.isValid()) {
            // @todo: Error report
            return;
        }
        if (data.id) { // @todo: phantom?
            // Change
            record = me.grid.getSelectionModel().getLastSelected();
            record.set(data);
        } else {
            // Create
            record = me.store.add([data])[0];
        }
        me.store.sync({
            scope: me,
            success: function() {
                this.toggle();
                this.reloadStore();
            },
            failure: function(response, op, status) {
                if(record.phantom) {
                    // Remove from store
                    me.store.remove(record);
                }
                this.showOpError("save", op, status);
            }
        });
    },
    // Show Form
    onEditRecord: function(view, record) {
        var me = this.up("panel");
        // Check permissions
        if (!me.hasPermission("read") && !me.hasPermission("update"))
            return;
        me.editRecord(record);
    },
    // New record. Hide grid and open form
    onNewRecord: function(defaults) {
        var me = this;
        me.form.reset();
        if(defaults) {
            me.form.setValues(defaults);
        }
        me.currentRecord = null;
        me.setFormTitle(me.createTitle);
        me.toggle();
        me.form.getFields().first().focus(false, 100);
        // Activate delete button
        me.deleteButton.setDisabled(true);
        me.saveButton.setDisabled(!me.hasPermission("create"));
        me.resetButton.setDisabled(!me.hasPermission("create"));
        // Disable custom form toolbar
        me.activateCustomFormToolbar(false);
    },
    // Edit record. Hide grid and open form
    editRecord: function(record) {
        var me = this;
        me.currentRecord = record;
        me.setFormTitle(me.changeTitle);
        // Show edit form
        me.toggle();
        // Load records
        me.form.loadRecord(record);
        // Focus on first field
        me.form.getFields().first().focus(false, 100);
        // Activate delete button
        me.deleteButton.setDisabled(!me.hasPermission("delete"));
        me.saveButton.setDisabled(!me.hasPermission("update"));
        me.resetButton.setDisabled(!me.hasPermission("update"));
        // Enable custom form toolbar
        me.activateCustomFormToolbar(true);
    },
    // Delete record
    deleteRecord: function() {
        var me = this,
            record = me.grid.getSelectionModel().getLastSelected();
        me.store.remove(record);
        me.store.sync();
        me.toggle();
    },
    // Reload store with current query
    reloadStore: function() {
        var me = this;
        if(me.currentQuery)
            me.store.setFilterParams(me.currentQuery);
        me.store.load();
    },
    // Search
    onSearch: function() {
        var me = this,
            v = me.search_field.getValue();
        if(v)
            me.currentQuery["__query"] = v;
        else
            delete me.currentQuery["__query"];
        me.reloadStore();
    },
    // Filter
    onFilter: function() {
        var me = this,
            fexp = {};
        Ext.each(me.filterGetters, function(g) {
            fexp = Ext.Object.merge(fexp, g());
        });
        if(me.currentQuery["__query"])
            fexp["__query"] = me.currentQuery["__query"];
        me.currentQuery = fexp;
        me.reloadStore();
    },
    // Save button pressed
    onSave: function() {
        var me = this;
        if(!me.form.isValid())
            return;
        var v = this.form.getFieldValues();
        // Fetch comboboxes labels
        me.form.getFields().each(function(field) {
            if(Ext.isDefined(field.getLookupData))
                v[field.name + "__label"] = field.getLookupData();
        });
        me.saveRecord(v);
    },
    // Reset button pressed
    onReset: function() {
        this.form.reset();
    },
    // Delete button pressed
    onDelete: function() {
        var me = this;
        Ext.Msg.show({
            title: "Delete record?",
            msg: "Do you wish to delete record? This operation cannot be undone!",
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if (button == "yes")
                    me.deleteRecord();
            }
        });
    },
    // Form hotkeys processing
    onFormSpecialKey: function(field, key) {
        var me = this;
        if (field.xtype != "textfield")
            return;
        switch(key.getKey()) {
            case Ext.EventObject.ENTER:
                key.stopEvent();
                me.onSave();
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                me.onReset();
                break;
        }
    },
    // Set form title
    setFormTitle: function(tpl) {
        var me = this;
        me.formTitle.update(Ext.String.format(tpl, me.appTitle));
    },
    //
    activateCustomFormToolbar: function(status) {
        var me = this,
            tb = me.saveButton.ownerCt,
            afterSep = false;
        tb.items.each(function(i) {
            if(afterSep) {
                if(i.setDisabled) {
                    i.setDisabled(!status);
                }
            } else {
                if(i.itemId === "custom_sep") {
                    afterSep = true;
                }
            }
        });
    },
    //
    onResetFilters: function() {
        var me = this;
        me.filterPanel.getForm().reset();
        me.onFilter();
    },
    //
    showOpError: function(action, op, status) {
        var text = Ext.String.format("Failed to {0}", action);
        if(status) {
            text = Ext.String.format("Failed to {0}!<br>{1}",
                action, status.message);
        }
        NOC.error(text);
    },
    // "close" button pressed
    onClose: function() {
        var me = this;
        me.toggle();
        me.reloadStore();
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store) {
        var me = this;
        if(me.rowClassField) {
            var c = record.get(me.rowClassField);
            if(c) {
                return c;
            } else {
                return "";
            }
        } else {
            return "";
        }
    }
});
