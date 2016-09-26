###
	Управление библиотеками сущностей.
###
Ext.define 'Report.controller.Library',
	extend: 'Ext.app.Controller'
	id: 'library'
	
	control:
		component:
			'libraryMain #list':
				select: 'updateDescription'
	
	privates:
	
		###
			Обновляет данные описания выбранной сущности.
			@param {Ext.view.View} list Список сущностей.
			@param {Ext.data.Record} record Данные сущности.
		###
		updateDescription: (list, record) ->
			list.up('libraryMain').down('#description').setData record.getData()