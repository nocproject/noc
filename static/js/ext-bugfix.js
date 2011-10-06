/*
 * ExtJS hotfixes
 */

// http://www.sencha.com/forum/showthread.php?136576-4.0.2-formBind-no-longer-functions/page2
// add a workaround for bug where boundItems aren't properly
// recalculated when necessary
// if there are 0 bound items, we will always recheck
Ext.form.Basic.override({
    getBoundItems : function() {
        var boundItems = this._boundItems;
        if (!boundItems || boundItems.getCount() == 0) {
            boundItems = this._boundItems = Ext.create('Ext.util.MixedCollection');
            boundItems.addAll(this.owner.query('[formBind]'));
        }
        return boundItems;
    }
});
