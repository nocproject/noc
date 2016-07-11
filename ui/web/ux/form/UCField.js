Ext.define('Ext.ux.form.UCField', {
    alias : 'plugin.ucfield',

    constructor :  function(config) {
        Ext.apply(this, config);
    },

    init : function(field) {
        field.setFieldStyle({ textTransform: 'uppercase' });
        Ext.apply(field, {
            _processRawValue : field.processRawValue,
            processRawValue : function(value) { return this._processRawValue(value).toUpperCase(); }
        });
    }
});
