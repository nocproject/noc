//---------------------------------------------------------------------
//  Inspector abstract class
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.inv.map.inspectors.Inspector');

Ext.define('NOC.inv.map.inspectors.Inspector', {
    extend: 'Ext.panel.Panel',

    requires: [
        'NOC.inv.map.Legend'
    ],

    title: undefined,
    scrollable: true,
    bodyStyle: {
        background: '#c0c0c0'
    },

    layout: 'border',
    miniPaper: null,
    width: 200,

    initComponent: function() {
        this.infoText = Ext.create("Ext.container.Container", {
            region: 'north'
        });

        this.legend = Ext.create('NOC.inv.map.Legend', {
            hidden: true,
            region: 'south'
        });

        this.miniMap = Ext.create('Ext.Component', {
            region: 'south',
            height: 300,
            border: 2,
            style: {
                borderColor: 'black',
                borderStyle: 'solid',
                background: "#ecf0f1"
            }
        });

        Ext.apply(this, {
            defaults: {
                padding: 4
            },
            items: [
                this.infoText,
                this.miniMap,
                this.legend
            ]
        });
        this.callParent();
    },

    preview: function(name, segmentId, objectId) {
        var url = '/inv/map/' + segmentId + '/info/' + name + '/';

        if(name === 'managedobject' || name === 'link') {
            url += objectId + '/';
        }

        if(this.miniPaper) {
            var w = this.width;
            var h = this.miniMap.getHeight();
        }
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: this,
            success: function(response) {
                var values = Ext.decode(response.responseText);
                this.update(values);
                this.enableButtons(values);
            }
        });
    },

    createMini: function(mapPanel){
        this.paperEl = this.miniMap.el.dom;
        this.paper = mapPanel.paper;
        var w = this.width;
        var h = this.miniMap.getHeight() - 10;

        this.miniPaper = new joint.dia.Paper({
            el: this.paperEl,
            height: h,
            width: w,
            model: mapPanel.graph,
            gridSize: 1,
            interactive: false
        });
        this.miniPaper.on('blank:pointerdown', function(evt, x, y) {
            mapPanel.items.first().scrollTo(x, y);
        });
    },

    onLegend: function() {
        this.visibleToggle(this.legend);
    },

    onMiniMap: function() {
        this.visibleToggle(this.miniMap);
    },

    visibleToggle: function(element) {
        if(element.isVisible()) {
            element.hide();
        } else {
            element.show()
        }
    },

    scaleContentToFit: function() {
        this.miniPaper.scaleContentToFit();
    },

    enableButtons: Ext.emptyFn
});