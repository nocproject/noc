//---------------------------------------------------------------------
// Segment inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.SegmentInspector");

Ext.define("NOC.inv.map.inspectors.SegmentInspector", {
    extend: "Ext.panel.Panel",
    title: "Segment Inspector",
    autoScroll: true,
    layout: "vbox",
    bodyStyle: {
        background: "#c0c0c0"
    },

    initComponent: function() {
        var me = this;

        me.infoText = Ext.create("Ext.container.Container", {
            padding: 4
        });
        Ext.apply(me, {
            items: [
                me.infoText
            ]
        });
        me.callParent();
    },

    preview: function(segmentId) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/map/" + segmentId + "/info/segment/",
            method: "GET",
            scope: me,
            mask: me,
            success: function(response) {
                me.applyData(Ext.decode(response.responseText))
            }
        });
    },

    applyData: function(data) {
        var me = this,
            t;

        t = "<b>Name:</b> " + Ext.htmlEncode(data.name);
        if(data.description && data.description.length) {
            t += "<br><b>Description:</b><br>" + Ext.htmlEncode(data.description);
        }
        if(data.objects) {
            t += "<br/><b>Objects: </b>" + data.objects;
        }
        me.infoText.setHtml(t);
    }
});
