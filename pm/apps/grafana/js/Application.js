//---------------------------------------------------------------------
// pm.grafana application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.grafana.Application");

Ext.define("NOC.pm.grafana.Application", {
    extend: "NOC.core.Application",
    appId: "pm.grafana",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            html: "<a href='/static/pkg/grafana/index.html' target='_blank'>Click</a> to open dashboard panel in new tab"
        });
        me.callParent();
    }
});
