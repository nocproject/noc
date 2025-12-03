//---------------------------------------------------
// ColorField:
// Color picker field based on HTML5 color input
// when make build is used, custom element 'color-input' 
//---------------------------------------------------
console.debug("Defining Ext.ux.form.ColorField");

Ext.define("Ext.ux.form.ColorField", {
  extend: "Ext.form.field.Text",
  alias: "widget.colorfield",
  
  triggers: {
    color: {
      scope: "this",
      handler: "onTriggerClick",
    },
  },
  
  colorPickerMode: "auto", // 'auto' | 'custom' | 'native'
  width: 190,
  regex: /^(#|0x)?[0-9A-Fa-f]+$/,
  regexText: __("Enter hex value starting with # or 0x"),

  afterRender: function(){
    this.callParent(arguments);
    var hasCustom = !!(window.customElements && customElements.get("color-input"));
    this._pickerKind = this.colorPickerMode === "custom" ? "custom"
      : this.colorPickerMode === "native" ? "native"
      : (hasCustom ? "custom" : "native");
    this.openMethod = this._pickerKind === "custom" ? "show" : "click";
    this.changeEvent = this._pickerKind === "custom" ? "change" : "input";
    
    if(this._pickerKind === "custom"){
      this.colorInput = Ext.DomHelper.append(this.bodyEl, {
        tag: "color-input",
        style: "position:absolute;width:0;height:0;overflow:hidden;border:0;padding:0;margin:0;",
        theme: "light",
        colorspace: "hex",
        value: "#ffffff",
      }, true);
      // Fix background image issue in some browsers, remove when color-input is fixed
      customElements.whenDefined("color-input").then(() => {
        this.colorInput.dom.shadowRoot.querySelector("select").style.backgroundImage = "none";
      });
    } else{
      this.colorInput = Ext.DomHelper.append(this.bodyEl, {
        tag: "input",
        type: "color",
        style: "position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none;",
      }, true);

    }
    this.colorInput.on(this.changeEvent, () => this.setValue(this.colorInput.dom.value));
    
    if(this.value){
      this.updateColorDisplay(this.value);
    }
  },

  onTriggerClick: function(){
    if(Ext.isEmpty(this.colorInput)){
      return;
    }
    this.colorInput.dom[this.openMethod]();
  },

  updateColorDisplay: function(hexColor){    
    this._suppressPickerEvent = true;
    if(this._pickerKind === "custom"){
      this.colorInput.dom.value = hexColor;
      this.colorInput.dom.colorspace = "hex";
    } else{
      this.colorInput.dom.value = hexColor;
    }
    this._suppressPickerEvent = false;
    this.setFieldStyle({
      color: this.getContrastColor(hexColor),
      backgroundColor: hexColor,
      backgroundImage: "none",
    });
  },

  setValue: function(value){
    if(this._suppressPickerEvent){
      return; 
    }
    var decimalValue = this.toDecimalColor(value);
    
    this.value = this.toHexColor(decimalValue);
    this.updateColorDisplay(this.value);
    this.callParent([this.value]);
  },

  toDecimalColor: function(value){
    var decimalValue;
    if(typeof value === "string"){
      if(value.indexOf("#") === 0){
        decimalValue = parseInt(value.substring(1), 16);
      } else if(value.indexOf("0x") === 0){
        decimalValue = parseInt(value.substring(2), 16);
      } else{
        decimalValue = parseInt(value, 10);
      }
    } else{
      decimalValue = value;
    }
    return decimalValue;
  },
  
  toHexColor: function(decimalValue){
    var hex = Number(decimalValue).toString(16);
    while(hex.length < 6){
      hex = "0" + hex;
    }
    return "#" + hex.toLowerCase();
  },

  rawToValue: function(){
    return this.toDecimalColor(this.rawValue) || 0;
  },

  getContrastColor: function(hexValue){
    var r = parseInt(hexValue.substr(1, 2), 16),
      g = parseInt(hexValue.substr(3, 2), 16),
      b = parseInt(hexValue.substr(5, 2), 16),
      avgBrightness = r * 0.299 + g * 0.597 + b * 0.114;
    return (avgBrightness > 130) ? "#000000" : "#FFFFFF";
  },

  onDestroy: function(){
    if(this.colorInput){
      this.colorInput.un(this.changeEvent, this.setValue);
      this.colorInput.destroy();
    }
    this.callParent(arguments);
  },
});