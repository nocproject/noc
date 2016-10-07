//---------------------------------------------------------------------
// Link inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.LinkInspector");

Ext.define("NOC.inv.map.inspectors.LinkInspector", {
    extend: "Ext.panel.Panel",

    requires: [],

    title: __("Link Inspector"),
    autoScroll: true,
    bodyStyle: {
        background: "#c0c0c0"
    },

    initComponent: function() {
        var me = this;

        me.infoText = Ext.create("Ext.container.Container", {
            padding: 4,
            region: 'north'
        });

        me.legendPicture = Ext.create('NOC.inv.map.Legend', {
            width: me.width,
            height: 335
        });

        me.legendText = Ext.create("Ext.container.Container", {
            padding: 4,
            region: 'south',
            autoShow: false,
            items: [
                {
                    xtype: 'box',
                    html: __('Legend')
                },
                me.legendPicture
            ]
        });
        // autoShow: false doesn't work
        me.legendText.hide();

        me.dashboardButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.line_chart,
            scope: me,
            tooltip: __("Show dashboard"),
            handler: me.onDashboard,
            disabled: true
        });

        me.legendButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.info,
            scope: me,
            tooltip: __("Show legend"),
            enableToggle: true,
            listeners: {
                scope: me,
                toggle: me.onLegend
            }
        });

        Ext.apply(me, {
            layout: 'border',
            items: [
                me.infoText,
                me.legendText
            ],
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.dashboardButton,
                    me.legendButton
                ]
            }]
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
            t, ut;

        t = "";
        Ext.each(data.objects, function(v) {
            var fmt;

            t += "<div class='noc-offset-0'><b>" + v.name + ":</b></div>";
            Ext.each(v.interfaces, function(i) {
                if(i.description) {
                    fmt = "<div class='noc-offset-1'>{0}: {1}</div><div class='noc-offset-2'>{2}</div>";
                } else {
                    fmt = "<div class='noc-offset-1'>{0}: {1}</div>";
                }
                t += Ext.String.format(
                    fmt,
                    Ext.htmlEncode(i.name),
                    i.status,
                    i.description
                );
            });
        });
        t += "<b>Discovery: </b>" + data.method + "<br>";
        // Utilisation
        ut = data.utilisation.map(function(v) {
            return parseInt(v / 1000000) + "Mbit/s";
        }).join(" | ");
        t += "<b>Util: </b>" + ut + "<br>";
        me.dashboardButton.setDisabled(false);
        me.infoText.setHtml(t);
        me.currentLinkId = data.id;
    },

    onDashboard: function() {
        var me = this;
        if(me.currentLinkId) {
            window.open(
                '/ui/grafana/dashboard/script/noc.js?dashboard=link&id=' + me.currentLinkId
            );
        }
    },

    onLegend: function(element, pressed) {
        if(pressed) {
            this.legendText.show()
        } else {
            this.legendText.hide();
        }
    }
});
