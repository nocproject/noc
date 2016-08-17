Ext.define 'Report.NocMenu',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'nocMenu'
	cls: 'noc-menu'

	items: [
		{
			xtype: 'tbtext'
			text: 'NOC | Отчеты'
		}
		'->'
		{
			itemId: 'userButton'
			xtype: 'button'
		}
	],

    setUserName: (name) ->
        this.up('#userButton').setText(name)