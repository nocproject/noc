//---------------------------------------------------------------------
// CPE object inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.CPEInspector");

Ext.define("NOC.inv.map.inspectors.CPEInspector", {
    extend: "NOC.inv.map.inspectors.Inspector",
    title: __("CPE Inspector"),
    inspectorName: "cpe",

    tpl: [
        '<b>Name:</b>&nbsp;{[Ext.htmlEncode(values.name)]}<br/>',
        '<b>Address:</b>&nbsp;{address}<br/>',
        '<tpl if="platform">',
        '<b>Platform:</b>&nbsp;{[Ext.htmlEncode(values.platform)]}<br/>',
        '</tpl>',
        '<tpl if="description">',
        '<b>Description:</b>&nbsp;{[Ext.htmlEncode(values.description)]}<br/>',
        '</tpl>'
    ],

    initComponent: function() {
        this.lookButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.pencil,
            scope: this,
            tooltip: __("Edit"),
            handler: this.onLook,
            disabled: true
        });

        this.cardButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.eye,
            scope: this,
            tooltip: __("View card"),
            handler: this.onMOCard,
            disabled: true
        });

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
                    this.cardButton,
                    this.lookButton,
                    this.dashboardButton
                ]
            }]
        });
        this.callParent();
        },

    onMOCard: function() {
        if(this.currentObjectId) {
            window.open(
                "/api/card/view/cpe/" + this.currentObjectId + "/"
                );
        }
    },

    onDashboard: function() {
        if(this.currentObjectId) {
            window.open(
                "/ui/grafana/dashboard/script/noc.js?dashboard=cpe&id=" + this.currentObjectId
                );
        }
    },

    enableButtons: function(data) {
        this.lookButton.setDisabled(false);
        this.cardButton.setDisabled(false);
        this.dashboardButton.setDisabled(false);

        this.currentObjectId = data.id;

    },

    getDataURL: function(segmentId, objectId) {
        var me = this,
            url = me.callParent([segmentId, objectId]);
        return url + objectId + "/";
    }
});
