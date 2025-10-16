Ext.define("Override.slider.Tip", {
  override: "Ext.slider.Tip",

  offsets: [0, 45],
  init: function(slider){
    var me = this;

    me.callParent([slider]);

    slider.on({
      scope: me,
      delay: 300,
      hideTip: me.hide,
      dragend: me.show,
      showTip: me.show,
      change: me.onSlide,
    });
  },
});

Ext.define("NOC.core.RevisionSlider", {
  extend: "Ext.panel.Panel",
  layout: "fit",
  maxValue: 0,
  value: 0,

  initComponent: function(){
    var me = this;

    this.viewModel = new Ext.app.ViewModel({
      max1: {
        get: function(){
          return me.maxValue;
        },

        set: function(value){
          me.maxValue = value;
        },
      },
      cur1: {
        get: function(){
          return me.value;
        },

        set: function(value){
          me.value = value;
        },
      },
    });
    me.slider = Ext.create("Ext.slider.Single", {
      fieldLabel: me.label,
      labelWidth: me.labelWidth,
      increment: 1,
      publishOnComplete: false,
      tipText: function(thumb){
        if(me.viewModel.get("sliderStore") && thumb && thumb.value !== -1){
          return Ext.Date.format(me.viewModel.get("sliderStore").getAt(thumb.value).get("ts"), "d.m.y H:i");
        } else{
          return "no data";
        }
      },
      minValue: 0,
      bind: {
        maxValue: "{max1}",
        value: "{cur1}",
      },

      listeners: {
        changecomplete: this.onChange,
      },
    });
    this.items = me.slider;
    this.callParent();
  },
  setStore: function(data){
    this.viewModel.set("sliderStore", Ext.create("Ext.data.Store", {
      sorters:
                {
                  property: "ts",
                  direction: "ASC",
                },
      fields: [
        {
          name: "ts",
          type: "date",
        },
      ],
      data: data,
    }));
    this.viewModel.set("max1", data.length - 1);
    this.viewModel.set("cur1", data.length - 1);
    this.slider.fireEvent("showTip");
  },
  getRevId: function(){
    return this.viewModel.get("sliderStore").getAt(this.viewModel.get("cur1")).get("id")
  },
});