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
    //vtype: "color",

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
                    backgroundColor: "#ffffff"
                },
                listeners: {
                    scope: me,
                    select: me.onSelectColor,
                    show: me.onShowPicker
                },
                colors: [
                    '1abc9c',
                    '2ecc71',
                    '3498db',
                    '9b59b6',
                    '34495e',
                    '16a085',
                    '27ae60',
                    '2980b9',
                    '8e44ad',
                    '2c3e50',
                    'f1c40f',
                    'e67e22',
                    'e74c3c',
                    'ecf0f1',
                    '95a5a6',
                    'f39c12',
                    'd35400',
                    'c0392b',
                    'bdc3c7',
                    '7f8c8d',
                    '000000',
                    'ffffff'
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

    toHexColor: function(x) {
        let hex = Number(x).toString(16);
        while(hex.length < 6) {
            hex = "0" + hex;
        }
        return "#" + hex;
    }
});
