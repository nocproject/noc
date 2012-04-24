//---------------------------------------------------------------------
// NOC.core.StateProvider - REST State provider
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.StateProvider");

Ext.define("NOC.core.StateProvider", {
    extend: "Ext.state.Provider",

    url: "/main/desktop/state/",

    constructor: function(config) {
        var me = this;
        me.callParent();
        me.state = me.loadPreferences();
        console.log("User preferences state: ", me.state);
    },

    loadPreferences: function() {
        var me = this;
        // Synchronous request
        var xmlhttp = new XMLHttpRequest();
        console.log("Requesting user preferences");
        xmlhttp.open("GET", me.url, false);
        xmlhttp.send(null);
        if(xmlhttp.status == 200) {
            var prefs = Ext.decode(xmlhttp.responseText);
            for(var k in prefs) {
                prefs[k] = me.decodeValue(prefs[k])
            }
            return prefs;
        }
    },

    set: function(name, value) {
        var me = this;
        me.callParent([name, value]);
        Ext.Ajax.request({
            url: me.url + name + "/",
            method: "POST",
            params: me.encodeValue(value)
        });
    },

    clear: function(name) {
        var me = this;
        me.callParent([name]);
        Ext.Ajax.request({
            url: me.url + name + "/",
            method: "DELETE"
        });
    }
});
