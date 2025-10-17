//---------------------------------------------------------------------
// NOC.core.modelfilter.Boolean
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Boolean");

Ext.define("NOC.core.modelfilter.Boolean", {
  extend: "NOC.core.modelfilter.AbstractRadioButton",

  constructor: function(config){
    this.clsYes = "noc-yes";
    this.clsNo = "noc-no";
    this.toggleGroup = "boolgroup";
    this.glyphYes = NOC.glyph.check;
    this.glyphNo = NOC.glyph.times;
    Ext.apply(this, config);
    this.callParent();
  },
});