//---------------------------------------------------------------------
// NOC.core.label.LabelDisplay -
// Label Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.label.LabelDisplay");

Ext.define("NOC.core.label.LabelDisplay", {
  extend: "Ext.form.field.Display",
  alias: "widget.labeldisplay",

  fieldSubTpl: [
    '<div id="{id}" data-ref="inputEl" tabindex="-1" role="textbox" aria-readonly="true"',
    ' aria-labelledby="{cmpId}-labelEl" {inputAttrTpl}',
    '<tpl if="fieldStyle"> style="{fieldStyle}"</tpl>',
    ' class="{fieldCls} {fieldCls}-{ui} label-display">{value}</div>',
    {
      compiled: true,
      disableFormats: true,
    },
  ],

  getDisplayValue: function(){
    var me = this,
      value = this.getRawValue(),
      display,
      chip = new Ext.XTemplate([
        '<tpl for=".">',
        '<tpl if="scope"><div style="display: block;" data-qtip="{scope}::{value}">',
        '<tpl else><div data-qtip="{value}"></tpl>',
        '<span class="noc-label-field-start" style="color: {fg_color1};background-color: {bg_color1};">{scope}</span>',
        '<span class="noc-label-field-end" style="color: {fg_color2};background-color: {bg_color2};">{value}</span>',
        "</div>",
        "</tpl>",
        {
          compiled: true,
          disableFormats: true,
        },
      ]);
    if(me.renderer){
      display = me.renderer.call(me.scope || me, value, me);
    } else{
      display = me.htmlEncode ? Ext.util.Format.htmlEncode(value) : value;
    }
    return chip.apply(display);
  },
});
