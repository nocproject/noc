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
			iconCls: 'x-fa fa-plus'
			text: 'Создать'
			margin: '2 10 2 2'
		}
		{
			itemId: 'copy'
			xtype: 'button'
			iconCls: 'x-fa fa-copy'
			text: 'Копировать'
			margin: '2 10 2 2'
		}
		{
			itemId: 'delete'
			xtype: 'button'
			iconCls: 'x-fa fa-trash'
			text: 'Удалить'
		}
		'->'
		{
			itemId: 'select'
			xtype: 'button'
			iconCls: 'x-fa fa-check'
			text: 'Выбрать'
		}
	]