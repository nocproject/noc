//---------------------------------------------------------------------
// Basket Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.inv.map.BasketController');

Ext.define('NOC.inv.map.BasketController', {
  extend: 'Ext.app.ViewController',
  alias: 'controller.basket',

  mixins: [
    "NOC.core.mixins.Export",
  ],

  onDeleteClick: function(){
    var grid = this.getView(),
      selected = grid.getSelectionModel().getSelection(),
      store = grid.getStore();

    store.remove(selected);
  },

  onDeleteAllClick: function(){
    this.getView().getStore().removeAll();
  },

  onCreateMaintainceClick: function(){
    var grid = this.getView();

    grid.fireEvent('createmaintaince', grid.getStore().getData());
  },

  onAddToMaintainceClick: function(){
    var grid = this.getView();

    grid.fireEvent('addtomaintaince', grid.getStore().getData());
  },

  onExportClick: function(){
    this.save(this.getView(),
              'basket.csv',
              [
                {dataIndex: 'object'},
                {dataIndex: 'address'},
                {dataIndex: 'platform'},
                {dataIndex: 'time'},

              ])
  },
});