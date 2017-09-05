//---------------------------------------------------------------------
// Mini Map
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.inv.map.MiniMap');

Ext.define('NOC.inv.map.MiniMap', {
    // extend: 'Ext.container.Container',
    extend: 'Ext.panel.Panel',
    alias: 'widget.minimap',

    height: 300,
    style: {
        background: "#ecf0f1"
    },
    miniPaper: null,
    items: {
        xtype: 'container'
    },

    createMini: function(mapPanel){
        this.paperEl = this.items.first().el.dom;
        this.paper = mapPanel.paper;
        var w = this.width;
        var h = this.height - 10;

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

    scaleContentToFit: function() {
        this.miniPaper.scaleContentToFit();
    }
});