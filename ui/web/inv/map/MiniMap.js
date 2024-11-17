//---------------------------------------------------------------------
// Mini Map
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MiniMap");

Ext.define("NOC.inv.map.MiniMap", {
  extend: "Ext.panel.Panel",
  alias: "widget.minimap",

  height: 300,
  miniPaper: null,
  items: {
    xtype: "container",
    height: 300,
  },

  createMini: function(mapPanel){
    var w = this.width,
      h = this.height - 10,
      scrollMap = function(){
        var [x, y] = Object.values(arguments).slice(-2),
          {sx, sy} = mapPanel.paper.scale();
        mapPanel.scrollTo(x * sx, y * sy);
      };
    this.paperEl = this.items.first().el.dom;
    this.paper = mapPanel.paper;

    this.miniPaper = new joint.dia.Paper({
      el: this.paperEl,
      height: h,
      width: w,
      model: mapPanel.graph,
      gridSize: 1,
      interactive: false,
    });

    this.miniPaper.on("cell:pointerdown", scrollMap);
    this.miniPaper.on("link:pointerdown", scrollMap);
    this.miniPaper.on("element:pointerdown", scrollMap);
    this.miniPaper.on("blank:pointerdown", scrollMap);
  },

  scaleContentToFit: function(){
    this.miniPaper.scaleContentToFit();
  },
});