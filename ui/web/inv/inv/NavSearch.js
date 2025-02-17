//---------------------------------------------------------------------
// inv.inv Nav Search field
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.NavSearch");

Ext.define("NOC.inv.inv.NavSearch", {
  extend: "Ext.form.field.ComboBox",
  xtype: "searchcombo",
  typeAhead: true,
  minChars: 3,
  queryDelay: 300,
  triggerAction: "query",
  valueField: "id",
  displayField: "path",
  hideTrigger: true,
  enableKeyEvents: true,
  queryMode: "remote",
  queryParam: "q",
  emptyText: __("search..."),
  forceSelection: false,
  store: {
    fields: ["path"],
    proxy: {
      type: "ajax",
      url: "/inv/inv/search/",
      reader: {
        type: "json",
        rootProperty: "items",
      },
      limitParam: undefined,
      pageParam: undefined,
      startParam: undefined,
    //   extraParams: {
    //     limit: 5,
    //   },
    },
  },
  listConfig: {
    loadingText: __("Search..."),
    emptyText: "<div class='noc-inv-nav-empty'>" + __("Nothing was found") + "</div>",
    minWidth: 800,
    padding: 4,
    tpl: [
      "<ul class='x-list-plain'><tpl for='.'>",
      "<li role='option'>",
      "<tpl for='path'>",
      "{[xindex > 1 ? '<span class=\"noc-inv-nav-search-separator\">/</span>' : '']}",
      "<span class='noc-inv-nav-label' data-id='{id}'>{label}</span>",
      "</tpl>",
      "</li>",
      "</tpl></ul>",
    ],
    listeners: {
      afterrender: function(list){
        var combo = list.up("searchcombo");
        list.getEl().on("click", function(e){
          var label = e.getTarget(".noc-inv-nav-label");
          if(label){
            var pathId = label.dataset.id;
            if(!Ext.isEmpty(pathId)){
              combo.fireEvent("invPathSelected", pathId);
              combo.collapse();
            }
          }
        });
      },
    },
  },
  triggers: {
    clear: {
      cls: "x-form-clear-trigger",
      handler: function(field){
        field.clearValue();
        field.collapse();
      },
    },
  },
  listeners: {
    change: function(field, newValue){
      var trigger = field.getTrigger("clear");
      if(trigger){
        trigger.setVisible(!Ext.isEmpty(newValue));
      }
    },
    keydown: function(field, e){
      if(e.getKey() === e.ESC){
        field.clearValue();
      }
    },
  },
});
