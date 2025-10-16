//---------------------------------------------------------------------
// NOC.core.modelfilter.Favorites
// Favorites model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Favorites");

Ext.define("NOC.core.modelfilter.Favorites", {
  extend: "NOC.core.modelfilter.AbstractRadioButton",

  constructor: function(config){
    this.clsYes = "noc-starred";
    this.clsNo = "noc-unstarred";
    this.toggleGroup = "favgroup";
    this.glyphYes = NOC.glyph.star;
    this.glyphNo = NOC.glyph.star;
    Ext.apply(this, config);
    this.callParent();
  },
});