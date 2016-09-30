###
	Тулбар управления библиотекой.
###
Ext.define 'Report.view.library.Control',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'libraryControl'
	
	items: [
		{
			itemId: 'create'
			xtype: 'button'
			text: 'Создать'
		}
		'->'
		{
			itemId: 'select'
			xtype: 'button'
			text: 'Выбрать'
		}
	]