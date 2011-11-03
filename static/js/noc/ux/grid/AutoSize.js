Ext.define('Ext.ux.grid.AutoSize', {
    alias : 'plugin.autosizegrid',

    constructor :  function(config) {
        Ext.apply(this, config);
    },

    init : function(gridpanel) {
        gridpanel.on('resize', this.onResize, this);
        gridpanel.getView().on('refresh', this.onRefresh, this);
    },

    onResize: function(gridpanel) {
        this.update_content(gridpanel.getView());
    },

    onRefresh: function(view) {
        this.update_content(view);
    },

    update_content: function(view) {
        var e = view.all.item(0);

        if(!e) { return; }

        var new_pageSize = Math.floor(view.getHeight()/e.getHeight());

        if (view.store.pageSize != new_pageSize) {
            view.store.pageSize = new_pageSize;
            view.store.load();
        }
    }
});
