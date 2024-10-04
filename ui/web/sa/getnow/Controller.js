//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.getnow.Controller');
Ext.define('NOC.sa.getnow.Controller', {
  extend: 'Ext.app.ViewController',
  alias: 'controller.getnow',

  mixins: [
    'NOC.core.mixins.Export',
  ],

  onShowFilter: function(){
    this.lookupReference('filterPanel').toggleCollapse();
  },

  onReload: function(){
    this.getViewModel().getStore('objectsStore').reload();
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
    this.lookupReference('repoPreview').preview(record);
  },

  onGetConfig: function(){
    var selected_devices = this.lookupReference('selectionGrid').getSelectionModel().getSelection();
    var pollingDevices = this.getViewModel().get('polling.devices');
    var viewModel = this.getViewModel();
    var store = this.getViewModel().getStore('objectsStore');
    var params = [];

    Ext.each(selected_devices, function(device){
      device.set('status', 'R');
      device.commit();
      pollingDevices.push(device.get('id'));
      params.push('ids=' + device.get('id'));
    });

    Ext.Ajax.request({
      url: '/sa/managedobject/actions/run_discovery/',
      method: 'POST',
      params: params.join('&'),
    }).then(function(){
      setTimeout(function(){
        var task = {
          run: function(){
            if(pollingDevices.length){
              Ext.Ajax.request({
                url: '/sa/getnow/',
                method: 'POST',
                jsonData: {ids: pollingDevices},
                success: function(response){
                  Ext.Array.each(JSON.parse(response.responseText), function(record){
                    var stored = store.getById(record.id);

                    if(stored){
                      stored.set('status', record.status);
                      stored.set('last_status', record.last_status);
                      stored.commit();

                      if(record.status !== 'R'){
                        var indx = pollingDevices.indexOf(record.id);
                        if(indx !== -1){
                          pollingDevices.splice(indx, 1);
                          viewModel.set('polling.leave', pollingDevices.length);
                        }
                      }
                    }
                  });
                },
                failure: function(data){
                  console.log(data);
                },
              });
            } else{
              viewModel.set('polling.style', 'noc-badge-waiting');
              return false;
            }
          },
          interval: 3000,
        };

        if(!viewModel.get('isStarted')){
          viewModel.set('polling.taskId', Ext.TaskManager.start(task));
          viewModel.set('polling.style', 'noc-badge-running');
        }
      }, 5000);

    });

    this.getViewModel().set('polling.leave', pollingDevices.length);
    this.onUnselectAll();
  },

  onStopPolling: function(){
    var taskId = this.getViewModel().get('polling.taskId');

    if(taskId){
      var store = this.getViewModel().getStore('objectsStore');

      Ext.TaskManager.stop(taskId);
      this.getViewModel().set('polling.style', 'noc-badge-waiting');
      Ext.each(this.getViewModel().get('polling.devices'), function(id){
        var device = store.getById(id);

        if(device){
          device.set('status', 'W');
          device.commit();
        }
      });
      this.getViewModel().set('polling.devices', []);
      this.getViewModel().set('polling.leave', 0);
    }
  },

  onCollapseFilter: function(){
    this.getViewModel().set('isFilterOpen', false);
  },

  onExpandFilter: function(){
    this.getViewModel().set('isFilterOpen', true);
  },

  onRenderStatus: function(value){
    var stateCodeToName = {
      W: 'Wait',
      R: 'Run',
      S: 'Stop',
      F: 'Fail',
      D: 'Disabled',
      true: 'OK',
      false: 'Fail',
    };

    return (stateCodeToName[value]) ? stateCodeToName[value] : value;
  },

  onRenderTooltip: function(value, metaData){
    metaData.tdAttr = 'data-qtip="' + value + '"';

    return value;
  },

  onExport: function(){
    this.save(this.lookupReference('selectionGrid'), 'getnow.csv');
  },
});
