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
    status: "A",
    managed_object: "",
    administrative_domain: "",
    resource_group: "",
    event_class: "",
    timestamp__gte: null,
    timestamp__lte: null,
  },
  pollingInterval: 30000,
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
  onAutoReloadToggle: function(button, pressed){
    button.setGlyph(pressed ? "xf021" : "xf05e");
    if(pressed){
      this.startPolling();
    }
    if(!pressed){
      this.stopPolling();
    }
  },
  onResetFilter: function(){
    this.initFilter(this.getViewModel());
  },
  dateValidator: function(){
    return true;
  },
  // Returns true if polling is locked
  isPollLocked: function(){
    return this.getView().gridPanel.getView().getScrollable().getPosition().y !== 0;
  },
  pollingTask: function(){
    var view = this.getView();
    // Poll only application tab is visible
    if(!view.isActiveApp()){
      return;
    }
    // Poll only when in grid preview
    if(view.getLayout().getActiveItem().itemId !== "fm-event-main"){
      return;
    }
    // Poll only if polling is not locked
    // comment by issue 896
    // if(!this.isPollLocked()) {
    view.store.reload();
    // }
  },
  startPolling: function(){
    if(this.pollingTaskId){
      this.pollingTask();
    } else{
      this.pollingTaskId = Ext.TaskManager.start({
        run: this.pollingTask,
        interval: this.pollingInterval,
        scope: this,
      });
    }
  },
  stopPolling: function(){
    var me = this;
    if(me.pollingTaskId){
      Ext.TaskManager.stop(me.pollingTaskId);
      me.pollingTaskId = null;
    }
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
      {key: "status"},
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
});
