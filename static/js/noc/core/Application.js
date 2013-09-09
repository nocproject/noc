//---------------------------------------------------------------------
// NOC.core.Application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Application");

Ext.define("NOC.core.Application", {
    extend: "Ext.panel.Panel",
    layout: "fit",
    permissions: {},  // User permissions

    constructor: function(options) {
        var me = this;
        // Initialize templates when exists
        me.appId = me.appId || options.noc.app_id;
        me.templates = NOC.templates[me.appId] || {};
        // Set up permissions before calling initComponent
        me.permissions = {};
        for(var p in options.noc.permissions) {
            me.permissions[options.noc.permissions[p]] = true;
        }
        // Fix custom fields regex
        if(options.noc.cust_form_fields) {
            Ext.iterate(options.noc.cust_form_fields, function(obj) {
                if(obj.regex) {
                    obj.regex = new RegExp(obj.regex);
                }
            });
        }
        me.appTitle = options.title;
        me.noc = options.noc;
        me._registeredItems = [];
        me.callParent(options);
    },
    //
    initComponent: function() {
        var me = this;
        me.on("afterrender", me.processCommands, me);
        me.callParent();
    },
    //
    hasPermission: function(name) {
        return this.permissions[name] === true;
    },
    // Filter items and hide not available
    applyPermissions: function(items) {
        var me = this;
        Ext.each(items, function(i) {
            if(Ext.isDefined(i.hasAccess) && !i.hasAccess(me)) {
                // Hide item
                i.hidden = true;
            }
        });
        return items;
    },
    // Register new item and return id
    registerItem: function(item) {
        var me = this,
            items = me._registeredItems,
            itemId = items.push(item) - 1;
        me._registeredItems = items;
        return itemId;
    },
    //
    showItem: function(index) {
        var me = this;
        if(index === null || index === undefined) {
            return undefined;
        }
        me.getLayout().setActiveItem(index);
        return me.items.items[index];
    },
    //
    getRegisteredItems: function() {
        var me = this;
        return me._registeredItems;
    },
    //
    processCommands: function() {
        var me = this;
        if(me.noc.cmd) {
            var cmd = me["onCmd_" + me.noc.cmd.cmd];
            if(cmd) {
                cmd.call(me, me.noc.cmd);
            }
        }
    }
});
