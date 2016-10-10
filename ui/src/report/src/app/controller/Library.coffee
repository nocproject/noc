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
			'libraryMain #control #create':
				click: 'updateDescriptionAfterControl'
			'libraryMain #control #edit':
				click: 'updateDescriptionAfterControl'
			'libraryMain #control #copy':
				click: 'updateDescriptionAfterControl'
			'libraryMain #control #delete':
				click: 'updateDescriptionAfterControl'
	
	privates:
	
		###
			Обновляет данные описания выбранной сущности.
			@param {Report.view.library.List} list Виджет списка сущностей.
			@param {Ext.data.Record} record Данные сущности.
		###
		updateDescription: (list, record) ->
			descriptionWidget = list.up('libraryMain').down('#description')
			name = record.get 'name'
			description = record.get 'description'
			
			descriptionWidget.setDescription name, description
			
		###
			Обновляет данные описания выбранной сущности сразу после совершения действий,
			предусмотренных обработчиками тулбара управления библиотекой.
			В случае множественного выбора отображает данные первой выбранной сущности.
			В случае отсутствия выбранного, например по причине пустоты списка,
			стирает данные описания.
			@param {Ext.button.Button} button Кнопка управления сущностью библиотеки.
		###
		updateDescriptionAfterControl: (button) ->
			setTimeout(
				() =>
					list = button.up('libraryMain').down('#list')
					selected = list.getSelected()
					firstSelected = selected[0] or Ext.create('Ext.data.Model')
					
					@updateDescription list, firstSelected
				0
			)