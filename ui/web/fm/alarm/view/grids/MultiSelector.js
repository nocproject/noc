//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.MultiSelector");

Ext.define("NOC.fm.alarm.view.grids.MultiSelector", {
  extend: "Ext.view.MultiSelector",
  alias: "widget.fm.alarm.multiselector",
  requires: [
    "Ext.view.MultiSelector",
    "NOC.fm.alarm.view.grids.MultiPanelController",
  ],
  config: {
    value: null,
  },
  twoWayBindable: [
    "value",
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
        sorters: "label",
        listeners: {
          datachanged: "onDataChanged",
        },
      },
    },
  },
  controller: "fm.alarm.multi",
  viewConfig: {
    deferEmptyText: false,
  },
  bind: {store: "{multiStore}"},
  fieldName: "label",
  fieldTitle: __("Name"),
  height: 200,
  scrollable: "y",
  search: {
    field: "label",
    reference: "multi-search",
    searchText: __("search..."),
    removeRowTip: __("Remove this item."),
    minWidth: 300,
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
              text: "Select All",
              handler: function(btn){
                var selector = btn.up("multiselector-search"),
                  store = selector.getSearchStore();
                selector.selectRecords(store.getRange().reverse())
              },
            },
            "->",
            {
              xtype: "button",
              text: "Deselect All",
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
    // selectRecords: function(records) {
    //     var displayFn = function(rec) {
    //             return rec.label;
    //         },
    //         searchGrid = this.lookupReference("searchGrid");
    //     if(!Ext.isArray(records)) {
    //         records = [
    //             records
    //         ];
    //     }
    //     searchGrid.getStore().loadData({
    //         label: records.map(displayFn).join(",")
    //     });
    // },
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
              flex: 1,
            }, {
              text: __("Type"),
              dataIndex: "type",
              flex: 1,
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
  initComponent: function(){
    this.search.store = this.searchStore;
    this.viewConfig.emptyText = this.emptyText;
    this.columns = [
      {
        text: __("Name"),
        dataIndex: "label",
        flex: 1,
      }, {
        text: __("Type"),
        dataIndex: "type",
        flex: 1,
      }, {
        width: 22,
        menuDisabled: true,
        tdCls: Ext.baseCSSPrefix + "multiselector-remove",
        processEvent: this.processRowEvent.bind(this),
        renderer: this.renderRemoveRow,
        updater: Ext.emptyFn,
        scope: this,
      },
    ];
    this.callParent();
  },
  setValue: function(value, skip){
    this.callParent([value]);
    if(!skip){
      this.setWidgetValues(arguments[0]);
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
        value[this.fieldName] = record.label;
        return Ext.create("Ext.data.Model", value);
      }, this,
      );
    store.loadRecords(records);
    this.getViewModel().set("array", data.array);
    this.getViewModel().set("include", data.include);
  },
  // override
  addTools: function(){
    this.addTool([
      {
        bind: {type: "{includeProfile}"},
        tooltip: __("Include/Exclude profile from list"),
        callback: this._onShowClick,
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
  _onShowClick: function(){
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

      if(store.getCount()){
        searchPopup.selectRecords(store.getRange());
      }
    }
    if(searchPopup.isVisible()){
      searchPopup.hidePopup();
    } else{
      searchPopup.showPopup(me);
    }
  },
});