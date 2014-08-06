Ext.define('Ext.ux.form.SearchField', {
    extend: 'Ext.form.field.Text',

    alias: 'widget.searchfield',

    scope: null,
    handler: null,
    emptyText: "Search...",
    // Auto-select
    typeAhead: false,
    typeAheadDelay: 200,
    // Minimum characters to search
    // when typeAhead == true
    minChars: 2,

    initComponent: function() {
        var me = this;
        me.lastChars = 0;
        me.callParent();
        me.on("specialkey", me.onSpecialKey, me);
        if(me.typeAhead) {
            me.on("change", me.onChange, me, {
                buffer: me.typeAheadDelay
            });
        }
    },
    //
    onSpecialKey: function(field, event) {
        var me = this,
            key = event.getKey();
        if(key == event.ENTER) {
            me.onSearch();
        } else if (key == event.ESC) {
            field.reset();
        }
    },
    //
    onChange: function() {
        var me = this,
            query = me.getValue(),
            ql = query.length;
        if(!ql || ql < me.lastChars || ql >= me.minChars) {
            Ext.callback(me.handler, me.scope || this, [query]);
        }
        me.lastChars = ql;
    },
    //
    onSearch: function() {
        var me = this,
            query = me.getValue();
        Ext.callback(me.handler, me.scope || this, [query]);
    }
});
