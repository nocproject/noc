//---------------------------------------------------------------------
// fm.event application controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.ApplicationController");

Ext.define("NOC.fm.event.ApplicationController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.event",
  filtersInitValues: {
    managed_object: "",
    administrative_domain: "",
    resource_group: "",
    event_class: "",
    timestamp__gte: null,
    timestamp__lte: null,
  },
  filterBinding: undefined,
  init: function(view){
    var viewModel = view.getViewModel();

    this.initFilter(viewModel);
    this.filterBinding = viewModel.bind({
      bindTo: "{filter}",
      deep: true,
    }, this.onChangeFilters, this);
    this.callParent();
  },
  initFilter: function(viewModel){
    viewModel.set("filter", Ext.clone(this.filtersInitValues));
  },
  destroy: function(){
    this.filterBinding.destroy();
  },
  onChangeFilters: function(data){
    var grid = this.getView().gridPanel,
      store = grid.getStore(),
      filter = this.serialize(data);
    grid.mask(__("Loading..."));
    store.getProxy().setExtraParams(filter);
    store.load({
      params: filter,
      callback: function(){
        grid.unmask();
      },
    });
  },
  onResetFilter: function(){
    this.initFilter(this.getViewModel());
  },
  dateValidator: function(){
    return true;
  },
  serialize: function(value){
    var filter = {"__format": "ext"},
      setParam = function(param){
        if(Ext.isEmpty(value[param.key])){
          return;
        }
        if(param.valueField){
          if(Ext.isArray(value[param.key])){
            if(value[param.key].length === 1){
              filter[param.key] = value[param.key][0][param.valueField];
            } else{
              Ext.Array.map(value[param.key], function(element, index){
                filter[param.key + index + "__in"] = element[param.valueField];
              })
            }
          } else{ // if use selection in binding
            filter[param.key] = value[param.key][param.valueField];
          }
        } else{
          filter[param.key] = value[param.key];
        }
      };

    Ext.each([
      // datetime
      {key: "timestamp__gte"},
      {key: "timestamp__lte"},
      // combo & tree
      {key: "managed_object", valueField: "id"},
      {key: "administrative_domain", valueField: "id"},
      {key: "resource_group", valueField: "id"},
      {key: "event_class", valueField: "id"},
    ], setParam);
    return filter;
  },
  onRefresh: function(){
    this.getView().store.reload();
  },
  togglePanel: function(targetPanel, forceExpand){
    var view = this.getView(),
      container = view.eastContainer,
      currentPanel = container.getLayout().getActiveItem();

    if(forceExpand === false){
      container.collapse();
      return;
    }

    if(container.collapsed){
      container.expand();
      container.getLayout().setActiveItem(targetPanel);
      return;
    }

    if(currentPanel !== targetPanel){
      container.getLayout().setActiveItem(targetPanel);
    } else if(forceExpand !== true){
      container.collapse();
    }
  },

  toggleFilter: function(){
    this.getView().down("grid").getSelectionModel().deselectAll();
    this.togglePanel(this.getView().filterPanel);
  },

  expandInspector: function(_, record){
    var inspectorPanel = this.getView().inspectorPanel;
    this.togglePanel(inspectorPanel, true);
    inspectorPanel.setRecord(record);
  },

  collapseInspector: function(){
    this.togglePanel(null, false);
  },

  toggleInspector: function(collapse){
    this.togglePanel(this.getView().inspectorPanel, !collapse);
  },
});
