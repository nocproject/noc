//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.MultiPanel");

Ext.define("NOC.fm.alarm.view.grids.MultiPanel", {
  extend: "Ext.panel.Panel",
  itemId: "fm-alarm-multi-panel",
  alias: "widget.fm.alarm.multipanel",
  controller: "fm.alarm.multipanel",
  requires: [
    "Ext.view.MultiSelectorSearch",
    "NOC.fm.alarm.view.grids.MultiPanelController",
    "NOC.fm.alarm.store.Profile",
  ],
  viewModel: {
    data: {
      popupHidden: true,
      include: true,
      array: [],
    },
    formulas: {
      popupState: function(get){
        return get("popupHidden") ? "expand" : "collapse";
      },
      includeProfile: function(get){
        return get("include") ? "plus" : "minus";
      },
    },
    stores: {
      multiStore: {
        listeners: {
          datachanged: "onDataChanged",
        },
      },
    },
  },
  config: {
    value: null,
    search: {
      xtype: "multiselector-search",
      width: 300,
      minWidth: 300,
      height: 200,
      store: {
        autoLoad: false,
      },
      field: "label",
      reference: "multi-search",
      searchText: __("search..."),
      removeRowTip: __("Remove this item."),
      listeners: {
        focusleave: function(){
          this.hidePopup();
        },
      },
      // override
      makeDockedItems: function(){
        return [
          {
            xtype: "toolbar",
            dock: "top",
            items: [
              {
                xtype: "textfield",
                reference: "searchField",
                hideFieldLabel: true,
                emptyText: this.searchText,
                triggers: {
                  clear: {
                    cls: Ext.baseCSSPrefix + "form-clear-trigger",
                    handler: "onClearSearch",
                    hidden: true,
                  },
                },
                listeners: {
                  change: "onSearchChange",
                  buffer: 300,
                },
              },
              "->",
              {
                xtype: "button",
                glyph: NOC.glyph.times_circle,
                listeners: {
                  scope: this,
                  click: function(){
                    this.hidePopup();
                  },
                },
              },
            ],
          },
          {
            xtype: "toolbar",
            dock: "bottom",
            items: [
              {
                xtype: "button",
                text: __("Select All"),
                handler: function(btn){
                  var selector = btn.up("multiselector-search"),
                    store = selector.getSearchStore();
                  selector.selectRecords(store.getRange().reverse())
                },
              },
              "->",
              {
                xtype: "button",
                text: __("Unselect All"),
                handler: function(btn){
                  var selector = btn.up("multiselector-search"),
                    store = selector.getSearchStore();
                  selector.deselectRecords(store.getRange())
                },
              },
            ],
          },
        ];
      },
      selectRecords: function(records){
        return this._records(records, "select");
      },
      deselectRecords: function(records){
        return this._records(records, "deselect");
      },
      _records: function(records, cmd){
        var searchGrid = this.lookupReference("searchGrid"),
          mapping = function(r){
            return searchGrid.getStore().getById(r.id)
          };
        if(!Ext.isArray(records)){
          records = [
            records,
          ];
        }
        return searchGrid.getSelectionModel()[cmd](records.map(mapping));
      },
      makeItems: function(){
        return [
          {
            xtype: "grid",
            reference: "searchGrid",
            trailingBufferZone: 2,
            leadingBufferZone: 2,
            viewConfig: {
              deferEmptyText: false,
              emptyText: __("No results."),
            },
            columns: [
              {
                text: __("Name"),
                dataIndex: "label",
                flex: 3,
                renderer: function(v, _, record){
                  if(record.get("icon")){
                    v = "<i class='" + record.get("icon") + "' aria-hidden='true'></i>&nbsp;" + v;
                  }
                  return v;
                },
              }, {
                text: __("Type"),
                dataIndex: "type",
                flex: 1,
                renderer: function(v){
                  var TYPE_MAP = {
                    Service: __("SRV"),
                    Subscribers: __("SUB"),
                  };
                  return NOC.render.Choices(TYPE_MAP)(v);
                },
              },
            ],
          },
        ];
      },
      hidePopup: function(){
        this.setHidden(true);
        this.up().getViewModel().set("popupHidden", true);
      },
      showPopup: function(owner){
        this.showBy(owner, "tl-tr?");
        this.up().getViewModel().set("popupHidden", false);
      },
    },
  },
  twoWayBindable: [
    "value",
  ],
  height: 53,
  bodyPadding: 5,
  fieldName: "label",
  initValues: {
    include: false,
    array: [],
  },
  initComponent: function(){
    this.config.search.store.type = this.searchStore;
    this.callParent();
    this.setWidgetValues({include: false, array: []});
  },
  //
  setValue: function(value, skip){
    this.callParent([value]);
    if(!skip){
      this.setWidgetValues(value);
    }
  },
  setWidgetValues: function(data){
    if(Ext.Object.isEmpty(data)){
      return;
    }
    var store = this.getViewModel().getStore("multiStore"),
      records = data.array.map(function(record){
        var value = {};
        value.id = record.id;
        value.type = record.type;
        value.icon = record.icon;
        value[this.fieldName] = record.label;
        return Ext.create("Ext.data.Model", value);
      }, this,
      );
    store.loadRecords(records);
    this.getViewModel().set("array", data.array);
    this.getViewModel().set("include", data.include);
  },
  getStore: function(){
    return this.getViewModel().getStore("multiStore");
  },
  convertSearchRecord: Ext.identityFn,
  convertSelectionRecord: Ext.identityFn,
  // override
  addTools: function(){
    this.addTool([
      {
        bind: {type: "{includeProfile}"},
        tooltip: __("Include/Exclude profile from list"),
        callback: this._onIncludeClick,
        scope: this,
      },
      {
        bind: {type: "{popupState}"},
        tooltip: __("Show/Hide search popup"),
        callback: this._onShowSearch,
        scope: this,
      },
    ]);
  },
  _onIncludeClick: function(){
    var newValue = !this.getViewModel().get("include");
    this.getViewModel().set("include", newValue);
    this.setValue({
      include: newValue,
      array: this.getViewModel().get("array"),
    }, true);
  },
  _onShowSearch: function(){
    var me = this, store,
      searchPopup = me.searchPopup;

    if(!searchPopup){
      store = me.getStore();
      searchPopup = Ext.merge({
        owner: me,
        field: me.fieldName,
        floating: true,
      }, me.getSearch());
      me.searchPopup = searchPopup = me.add(searchPopup);

      searchPopup.lookupReference("searchGrid").getStore().load({
        callback: function(){
          if(store.getCount()){
            searchPopup.selectRecords(store.getRange());
          }
        },
      })
    }
    if(searchPopup.isVisible()){
      searchPopup.hidePopup();
    } else{
      searchPopup.showPopup(me);
    }
  },
  getInitValues: function(){
    return Ext.clone(this.initValues);
  },
});