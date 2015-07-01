//---------------------------------------------------------------------
// Link inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.LinkInspector");

Ext.define("NOC.inv.map.inspectors.LinkInspector", {
    extend: "Ext.panel.Panel",
    title: "Link Inspector",
    autoScroll: true,
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

    preview: function(segmentId, linkId) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/map/" + segmentId + "/info/link/" + linkId + "/",
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

        t = "";
        Ext.each(data.objects, function(v) {
            t += "<b>" + v.name + ":</b><br>";
            Ext.each(v.interfaces, function(i) {
                t += "&nbsp;&nbsp;" + Ext.htmlEncode(i.name);
                if(i.description) {
                    t += " (" + Ext.htmlEncode(i.description) + ")";
                }
                t += "<br>";
            });
        });
        t += "<b>Discovery: </b>" + data.method + "<br>";
        me.infoText.setHtml(t);
        me.currentLinkId = data.id;
    },
});
