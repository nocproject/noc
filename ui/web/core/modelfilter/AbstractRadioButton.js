//---------------------------------------------------------------------
// NOC.core.modelfilter.AbstractRadioButton
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.AbstractRadioButton");

Ext.define("NOC.core.modelfilter.AbstractRadioButton", {
  extend: "NOC.core.modelfilter.Base",
  layout: {
    type: "hbox",
  },
  initComponent: function(){
    var me = this;
    Ext.applyIf(me, {
      items: [
        {
          xtype: "displayfield",
          fieldLabel: me.title,
          allowBlank: true,
          flex: 2,
        },
        {
          xtype: "button",
          glyph: me.glyphYes,
          cls: me.clsYes,
          toggleGroup: me.toggleGroup,
          scope: me,
          handler: Ext.pass(me.onClickBtn, true),
        },
        {
          xtype: "button",
          glyph: me.glyphNo,
          cls: me.clsNo,
          toggleGroup: me.toggleGroup,
          scope: me,
          handler: Ext.pass(me.onClickBtn, false),
        },
      ],
    });

    me.callParent();
    me._value = undefined;
  },
  onClickBtn: function(isTrue, button){
    var me = this;
    me._value = button.pressed ? isTrue : undefined;
    me.onChange();
  },
  getFilter: function(){
    var me = this,
      r = {};

    if(me._value !== undefined)
      r[me.name] = me._value;

    return r;
  },
  setFilter: function(filter){
    var me = this;

    if(me.name in filter){
      var filterValue = filter[me.name];
      me._value = filter[me.name];
      Ext.each(me.items.items, function(button){
        var isButton = button.cls
          , isYesButton = isButton === me.clsYes
          , isNoButton = isButton === me.clsNo;
        if(isButton){
          if(isYesButton && filterValue === "true"){
            button.toggle(true);
          }
          if(isNoButton && filterValue === "false"){
            button.toggle(true);
          }
        }
      });
    }
  },
});