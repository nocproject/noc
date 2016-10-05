###
	Управление библиотеками сущностей.
###
Ext.define 'Report.controller.Library',
	extend: 'Ext.app.Controller'
	id: 'library'
	
	listen:
		component:
			'libraryMain #list':
				select: 'updateDescription'
	
	privates:
	
		###
			Обновляет данные описания выбранной сущности.
			@param {Report.view.library.List} list Виджет списка сущностей.
			@param {Ext.data.Record} record Данные сущности.
		###
		updateDescription: (list, record) ->
			description = list.up('libraryMain').down('#description')
			data = record.getData()
			
			description.setDescription data.name, data.description