//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.core.filter.ViewModel");
Ext.define("NOC.core.filter.ViewModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.core.filter",

  requires: [
    "NOC.core.filter.CapabilityModel",
  ],

  data: {
    filterObject: {},
  },

  stores: {
    capabilityStore: {
      model: "NOC.core.filter.CapabilityModel",
      xclass: "Ext.data.TreeStore",
      autoLoad: true,
      proxy: {
        type: "ajax",
        url: "/inv/capability/tree",
        reader: "json",
      },
      sorters: [
        {
          property: "leaf",
          direction: "ASC",
        }, {
          property: "text",
          direction: "ASC",
        },
      ],
      listeners: {
        load: "restoreFilter",
        update: "onChangeCapRecord",
      },
    },
  },

  formulas: {
    isLeaf: function(get){
      var selection = get("capabilitiesTree.selection");

      return selection && selection.get("leaf");
    },

    selectedCap: function(get){
      var selection = get("capabilitiesTree.selection");

      if(selection && selection.get("leaf")){
        return __("Selected") + " (" + selection.get("type") + "): "
                    + selection.getPath("text")
                        .split("/")
                        .filter(function(e){
                          return e.length > 0 && e !== "Root"
                        }).join(" | ");
      }
      return __("No leaf selected");
    },

    isTypeInclude: function(get){
      var selection = get("capabilitiesTree.selection");

      return selection && selection.get("typeInclude") && selection.get("type") !== "bool";
    },

    isTypeIncludeBool: function(get){
      var selection = get("capabilitiesTree.selection");

      return selection && selection.get("typeInclude") && selection.get("type") === "bool";
    },

    isTypeIncludeCondition: function(get){
      var selection = get("capabilitiesTree.selection");

      return selection && selection.get("typeInclude") && selection.get("type") === "int";
    },
  },
});