//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.ContainerModel");

Ext.define("NOC.fm.alarm.view.grids.ContainerModel", {
  extend: "Ext.app.ViewModel",
  alias: "viewmodel.fm.alarm.container",
  data: {
    total: {
      alarmsTotal: 0,
      selected: [],
      selectionFiltered: [],
      objects: 0,
      objectsFiltered: 0,
      activeAlarmsSelected: null,
    },
    volume: false,
    autoReload: true,
    icon: "<i class='fa fa-fw' style='padding-left:4px;width:16px;'></i>",
  },
  formulas: {
    alarmsTotal: function(get){
      return __("Total: ") + get("total.alarmsTotal");
    },
    summaryTotal: function(get){
      var selected = get("total.selected"),
        displayFilter = get("displayFilter.hasProfiles");
      return this.getView().getController().generateSummaryHtml(
        selected.filter(function(item){
          return item.summary > 0;
        }),
        displayFilter,
        true,
      );
    },
    summaryFiltered: function(get){
      var selected = get("total.selectionFiltered"),
        displayFilter = get("displayFilter.hasProfiles");
      return this.getView().getController().generateSummaryHtml(
        selected.filter(function(item){
          return item.summary > 0;
        }),
        displayFilter,
        true,
      );
    },
    showSummaryTotal: function(get){
      var selected = get("total.selected");
      return selected.filter(function(item){
        return item.summary > 0;
      }).length > 0;
    },
    isActiveAlarmsSelected: function(get){
      return get("total.activeAlarmsSelected") == null;
    },
    activeFilterIsClosed: function(get){
      return get("activeFilter.status") === "C";
    },
    volumeIcon: function(get){
      // NOC.glyph.volume_up or NOC.glyph.volume_off
      return get("volume") ? "xf028" : "xf026";
    },
    autoReloadIcon: function(get){
      //  NOC.glyph.refresh or NOC.glyph.ban
      return get("autoReload") ? "xf021" : "xf05e";
    },
    autoReloadText: function(get){
      return __("Auto reload : ") + (get("autoReload") ? __("ON") : __("OFF"));
    },
  },
});
