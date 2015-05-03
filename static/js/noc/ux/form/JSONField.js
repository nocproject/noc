Ext.define('Ext.ux.form.JSONField', {
    extend: 'Ext.form.field.Text',
    alias: "widget.jsonfield",
    vtype: "json",

    setValue: function(v) {
        var me = this;
        me.callParent([Ext.encode(v)]);
    },

    getValue: function() {
        var me = this;
        return Ext.decode(me.callParent());
    }
});
