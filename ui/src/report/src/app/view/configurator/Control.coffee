###
	Тулбар управления конфигуратором.
###
Ext.define 'Report.view.configurator.Control',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'configuratorControl'
	
	items: [
		'->'
		{
			itemId: 'save'
			xtype: 'button'
			text: 'Сохранить'
		}
	]