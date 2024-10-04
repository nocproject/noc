//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.monitor.Controller');
Ext.define('NOC.sa.monitor.Controller', {
  extend: 'Ext.app.ViewController',
  alias: 'controller.monitor',
  pollingTaskId: null,
  pollingInterval: 300000, // msec

  mixins: [
    'NOC.core.mixins.Export',
  ],

  onShowFilter: function(){
    this.lookupReference('filterPanel').toggleCollapse();
  },

  onSelectionChange: function(element, selected){
    this.getViewModel().set('total.selection', selected.length);
  },

  onSelectAll: function(){
    var selectionGrid = this.lookupReference('selectionGrid');
    var renderPlugin = selectionGrid.findPlugin('bufferedrenderer');

    selectionGrid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
  },

  onUnselectAll: function(){
    this.lookupReference('selectionGrid').getSelectionModel().deselectAll();
  },

  onRowDblClick: function(grid, record){
    this.getView().lookupReference('logPanel').load(record);
  },

  onRenderStatus: function(value){
    var stateCodeToName = {
      W: 'Wait',
      R: 'Run',
      S: 'Stop',
      F: 'Fail',
      D: 'Disabled',
    };

    return (stateCodeToName[value]) ? stateCodeToName[value] : value;
  },

  onRenderTooltip: function(value, metaData){
    metaData.tdAttr = 'data-qtip="' + value + '"';

    return value;
  },

  onExport: function(){
    this.save(this.lookupReference('selectionGrid'), 'monitor.csv');
  },

  onReload: function(btn){
    if(btn.pressed){
      this.startPolling();
    } else{
      this.stopPolling();
    }
  },

  pollingTask: function(){
    var logPanel = this.getView().lookupReference('logPanel'),
      grid = this.getView().lookupReference('grid');
    grid.mask(__('Loading...'));
    this.getViewModel().getStore('objectsStore').load(
      function(){
        grid.unmask();
      },
    );
    if(!logPanel.collapsed){
      logPanel.load();
    }
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
    if(this.pollingTaskId){
      Ext.TaskManager.stop(this.pollingTaskId);
      this.pollingTaskId = null;
    }
  },
});
