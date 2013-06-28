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
        me.appTitle = options.title;
        me.noc = options.noc;
        me.callParent(options);
    },
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
    }
});
