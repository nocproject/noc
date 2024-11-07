//---------------------------------------------------
// ColorField:
// ComboBox with color picker
// Based on
// http://www.learnsomethings.com/2012/03/20/extjs4-color-picker-in-a-drop-down-control-for-use-on-forms-and-in-editable-grids/
//---------------------------------------------------
console.debug("Defining Ext.ux.form.ColorField");

Ext.define("Ext.ux.form.ColorField", {
    extend: 'Ext.form.field.Text',
    alias: 'widget.colorfield',
    triggers: {
        color: {
            scope: "this",
            handler: "onTriggerClick"
        }
    },
    width: 190,
    regex: /^(#|0x)?[0-9A-Fa-f]+$/,
    regexText: __("Enter integer number or hex value starting with # or 0x"),

    onTriggerClick: function() {
        var me = this;
        if(!me.picker) {
            me.picker = Ext.create("Ext.picker.Color", {
                pickerField: me,
                ownerCt: me,
                floating: true,
                hidden: true,
                focusOnShow: true,
                defaultAlign: "tl-bl",
                alignTarget: me.inputEl,
                style: {
                    backgroundColor: "#FFFFFF"
                },
                listeners: {
                    scope: me,
                    select: me.onSelectColor,
                    show: me.onShowPicker
                },
                colors: [
                    '1ABC9C',
                    '2ECC71',
                    '3498DB',
                    '9B59B6',
                    '34495E',
                    '16A085',
                    '27AE60',
                    '2980B9',
                    '8E44AD',
                    '2C3E50',
                    'F1C40F',
                    'E67E22',
                    'E74C3C',
                    'ECF0F1',
                    '95A5A6',
                    'F39C12',
                    'D35400',
                    'C0392B',
                    'BDC3C7',
                    '7F8C8D',
                    '000000',
                    'FFFFFF'
                ]
            });
        }
        me.picker.show(me.inputEl);
    },

    onSelectColor: function(field, value, opts) {
        var me = this;
        me.setValue(parseInt(value, 16));
        me.picker.hide();
    },

    onShowPicker: function(field, opt) {
        field.getEl().monitorMouseLeave(500, field.hide, field);
    },
    // Set field color
    setColor: function(color) {
        var me = this;
        me.setFieldStyle({
            color: this.getContrastColor(color),
            backgroundColor: this.toHexColor(color),
            backgroundImage: "none"
        });
    },
    //
    setValue: function(value) {
        var me = this;
        me.callParent([value]);
        me.setColor(value);
    },
    //
    toHexColor: function(x) {
        let hex = Number(x).toString(16);
        while(hex.length < 6) {
            hex = "0" + hex;
        }
        return "#" + hex.toUpperCase();
    },
    //
    getValue: function() {
        var me = this;
        return me.toHexColor(me.callParent());
    },
    //
    getContrastColor: function(color) {
        var avgBrightness = ((color >> 16) & 255) * 0.299 + ((color >> 8) & 255) * 0.587 + (color & 255) * 0.114;
        return contrastColor = (avgBrightness > 130) ? '#000000' : '#FFFFFF';
    }
});