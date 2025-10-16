//---------------------------------------------------------------------
// NOC.core.modelfilter.GeoAddress
// Geo Address lookup model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.GeoAddress");

Ext.define("NOC.core.modelfilter.GeoAddress", {
  extend: "NOC.core.modelfilter.Base",
  name: "__geoaddress",

  initComponent: function(){
    var me = this;
    me.combo = Ext.create("NOC.gis.geocoder.LookupField", {
      fieldLabel: me.title,
      labelAlign: "top",
      width: me.width,
      typeAheadDelay: 500,
      minChars: 4,
      pageSize: 0,
      hideTrigger: true,
      listeners: {
        scope: me,
        select: me.onChange,
        clear: me.onChange,
      },
      dataFields: ["id", "label", "style", "is_loose"],
      tpl:
        '<tpl for=".">' +
        '<div class="x-boundlist-item {style}">{label}</div>' +
        "</tpl>",
    });
    Ext.apply(me, {
      items: [me.combo],
    });
    me.callParent();
  },

  getFilter: function(){
    var me = this,
      v = me.combo.getValue(),
      r = {};
    if(v){
      r[me.name] = v;
    }
    return r;
  },

  setFilter: function(filter){
    var me = this;
    if(me.name in filter){
      me.combo.setValue(filter[me.name]);
    }
  },
});
