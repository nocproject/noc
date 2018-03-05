//---------------------------------------------------------------------
// Link inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.LinkInspector");

Ext.define("NOC.inv.map.inspectors.LinkInspector", {
    extend: "NOC.inv.map.inspectors.Inspector",
    title: __("Link Inspector"),
    inspectorName: "link",

    tpl:[
        '<tpl if="name"><div style="font-weight: bold;text-decoration: underline">{name}</div></tpl>',
        '<tpl if="description"><div style="font-style: italic">{description}</div></tpl>',
        '<tpl for="objects">',
            '<div class="noc-offset-0"><b>{name}:&nbsp;</b></div>',
            '<tpl for="interfaces">',
                '<div class="noc-offset-1">{name}:&nbsp;{status}</div>',
                '<tpl if="description">',
                    '<div class="noc-offset-2">{description}</div>',
                '</tpl>',
            '</tpl>',
        '</tpl>',
        '<b>Discovery:&nbsp;</b>{method}<br>',
        '<b>Util:&nbsp;</b>{[this.utilization(values.utilisation, parent)]}<br/>',
        {
            utilization: function(values) {
                return values.map(function(v) {
                    return parseInt(v / 1000000) + "Mbit/s";
                }).join(" | ");
            }
        }
    ],

    initComponent: function() {
        this.dashboardButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.line_chart,
            scope: this,
            tooltip: __("Show dashboard"),
            handler: this.onDashboard,
            disabled: true
        });

        Ext.apply(this, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    this.dashboardButton
                ]
            }]
        });
        this.callParent();
    },

    onDashboard: function() {
        if(this.currentLinkId) {
            window.open(
                '/ui/grafana/dashboard/script/noc.js?dashboard=link&id=' + this.currentLinkId
            );
        }
    },

    enableButtons: function(values) {
        this.currentLinkId = values.id;
        this.dashboardButton.setDisabled(false);
    },

    getDataURL: function(segmentId, objectId) {
        var me = this,
            url = me.callParent([segmentId, objectId]);
        return url + objectId.split("-")[0] + "/";
    }
});
