###
	Набор мета-данных описания выбранной сущности.
###
Ext.define 'Report.view.library.Description',
	extend: 'Ext.container.Container'
	xtype: 'libraryDescription'
	
	layout: 'fit'
	
	items: [
		{
			itemId: 'tpl'
			xtype: 'component'
			padding: '25 20'
			tpl: '<div class="description">{description}</div>'
		}
	]
	
	###
		Устанавливает описание сущности.
		@param {String} name Имя.
		@param {String} description Описание.
	###
	setDescription: (name, description) ->
		@down('#tpl').setData {
			name
			description
		}
		