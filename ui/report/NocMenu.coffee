Ext.define 'Report.NocMenu',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'nocMenu'

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