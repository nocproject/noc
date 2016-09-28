###
	Управление логикой фильтров.
###
Ext.define 'Report.controller.Filter',
	extend: 'Ext.app.Controller'
	id: 'filter'

	listen:
		component:
			'[filterSing]':
				change: 'updateReportData'

	###
		Обновляет данные отчета.
	###
	updateReportData: (field) ->

		###
			Оповещает об необходимости обновить данные отчета используя фильтр.
			@param {Report.controller.FilterReport.controller.Filter} this Этот контроллер.
			@param {Report.model.config.Filter} model Модель фильтра.
			@param {Ext.form.field.Base} field Поле-инициатор.
		###
		@fireEvent 'updateReportDataByFilter', @, field.filterSing.model, field