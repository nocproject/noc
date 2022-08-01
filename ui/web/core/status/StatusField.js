//---------------------------------------------------------------------
// NOC.core.status.StatusField -
// status Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.status.StatusField");

Ext.define("NOC.core.status.StatusField", {
  extend: "Ext.form.field.Display",
  requires: [],
  alias: "widget.statusfield",

  fieldSubTpl: [
    '<div id="{id}" data-ref="inputEl" tabindex="-1" role="textbox" aria-readonly="true"',
    ' aria-labelledby="{cmpId}-labelEl" {inputAttrTpl}',
    '<tpl if="fieldStyle"> style="{fieldStyle}"</tpl>',
    ' class="{fieldCls} {fieldCls}-{ui} label-display"',
    ' style="display: flex;flex-wrap: wrap;align-items: flex-start;">{value}</div>',
    {
      compiled: true,
      disableFormats: true
    }
  ],
//  <tpl if="{error}}">({error})</tpl>
  getDisplayValue: function() {
    var me = this,
      value = this.getRawValue(),
      display,
      chip = new Ext.XTemplate([
        '<tpl for=".">',
        '<span class="noc-state-field noc-state-{state}"',
        '<tpl if="details.length &gt; 0">',
        'data-qtip="{[this.tip(values)]}"',
        // '<tpl for="details">data-qtip="{name}: {state}<br/>"</tpl>',
        '</tpl>',
        '>{[this.strip(values)]}</span>',
        '</tpl>',
        {
          disableFormats: true,
          strip: function(value) {
            var maxChar = 7;
            return value.name.length > maxChar ? value.name.substring(0, maxChar) : value.name;
          },
          tip: function(value) {
            var tip = "",
              details = value.details;
            for(var i = 0; i < details.length; i++) {
              tip += "<div>" + details[i].name + " : " + details[i].state;
              if(details[i].error) {
                tip += " (" + details[i].error + ")";
              }
              tip += "</div>";
            }
            return tip;
          }
        }
      ]);
    if(me.renderer) {
      display = me.renderer.call(me.scope || me, value, me);
    } else {
      display = me.htmlEncode ? Ext.util.Format.htmlEncode(value) : value;
    }
    return chip.apply(display);
  },
});