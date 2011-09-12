//---------------------------------------------------------------------
// Resizable IFrame tab for legacy applications
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.IFramePanel");

Ext.define("NOC.main.desktop.IFramePanel", {
    extend: "Ext.Panel",
    initComponent: function() {
        this.items = [{
            html: "<iframe style='border: none; width: 100%; height: 100%' src='" + this.noc.url + "'/>"
        }];
        NOC.main.desktop.IFramePanel.superclass.initComponent.call(this);
        this.on("resize", this.on_resize);
    },
    //
    on_resize: function() {
        // @todo: calculate IFRAME size properly
        var iframe = this.items.first().el.down("iframe");
        iframe.setWidth(this.getWidth());
        iframe.setHeight(this.getHeight());
    }
});
