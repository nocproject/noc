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
    vtype: "color",

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
                }
            });
        }
        me.picker.show(me.inputEl);
    },

    onSelectColor: function(field, value, opts) {
        var me = this;
        me.setValue(value);
        me.picker.hide();
    },

    onShowPicker: function(field, opt) {
        field.getEl().monitorMouseLeave(500, field.hide, field);
    },
    // Set field color
    setColor: function(color) {
        var me = this;
        me.setFieldStyle({
            backgroundColor: "#" + color,
            backgroundImage: "none"
        });
    },
    //
    setValue: function(value) {
        var me = this;
        me.callParent([value]);
        me.setColor(value);
    }
});
