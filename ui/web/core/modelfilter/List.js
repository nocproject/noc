//---------------------------------------------------------------------
// NOC.core.modelfilter.List
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.core.modelfilter.List");
Ext.define("NOC.core.modelfilter.List", {
  extend: "NOC.core.modelfilter.Base",

  constructor: function(config){
    Ext.apply(this, config);
    this.callParent();
  },
  //
  initComponent: function(){
    var me = this;
    // me.checkValue = Ext.create("Ext.form.field.Checkbox", {
    //     fieldLabel: __('Value'),
    //     listeners: {
    //         scope: me,
    //         change: me.onCheckClick
    //     }
    // });
    me.checkValue = Ext.create("Ext.form.ComboBox", {
      fieldLabel: __("Value"),
      labelAlign: "left",
      width: me.width,
      store: me.valuesStore,
      queryMode: "local",
      displayField: "label",
      valueField: "value",
      editable: false,
      listeners: {
        scope: me,
        select: me.onChangeValue,
      },
    });
    me.comboBox = Ext.create("Ext.form.ComboBox", {
      fieldLabel: me.title,
      labelAlign: "top",
      width: me.width,
      store: me.listStore,
      queryMode: "local",
      displayField: "label",
      valueField: "field_name",
      editable: false,
      listeners: {
        scope: me,
        select: me.onChangeField,
        clear: me.onClearField,
      },
    });
    Ext.applyIf(me, {
      items: [
        me.comboBox,
        me.checkValue,
      ],
    });

    me.callParent();
    me._value = undefined;
  },
  //
  getFilter: function(){
    var me = this,
      r = {};

    if(me.comboBox.getValue() && me.checkValue.getValue() !== "all")
      r[me.name] = me._value;

    return r;
  },
  //
  setFilter: function(filter){
    var me = this;
    for(var field_name in filter){
      if(me.listStore.data.filter(function(e){
        return e.field_name === field_name
      }).length > 0){
        //
        me.name = field_name;
        switch(filter[field_name]){
          case "true":
            me._value = true;
            break;
          case "false":
            me._value = false;
            break;
            // case "all":
            //     me._value = undefined;
            //     break;
          default:
            me._value = filter[field_name];
        }
        //
        me.comboBox.setValue(me.name);
        me.checkValue.setValue(me._value);
      }
    }
  },
  //
  onClearField: function(){
    this.checkValue.setValue(false);
    this._value = undefined;
  },
  //
  onChangeField: function(){
    this.name = this.comboBox.getValue();
    if(this._value !== undefined){
      this.onChange();
    }
  },
  //
  onChangeValue: function(){
    this._value = this.checkValue.getValue();
    if(this.comboBox.getValue()){
      if(this._value === "all"){
        this.name = undefined;
        this._value = undefined;
      } else{
        this.name = this.comboBox.getValue();
      }
      this.onChange();
    }
  },
  //
  // onClean: function() {
  //     this.name = undefined;
  //     this._value = undefined;
  //     //
  //     this.comboBox.setValue(null);
  //     this.checkValue.setValue(false);
  //     this.onChange();
  // }
});
