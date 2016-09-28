###
	Набор мета-данных описания выбранной сущности.
###
Ext.define 'Report.view.library.Description',
	extend: 'Ext.container.Container'
	xtype: 'libraryDescription'
	
	layout: 'fit'
	
	items: [
		{
			xtype: 'component'
			tpl: '
				<div class="title">{name}</div>
				<div class="description">{description}</div>
			'
		}
	]
		