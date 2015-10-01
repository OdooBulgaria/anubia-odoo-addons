# TO DO

- [x] Translate it
- [x] Spellchecking
- [ ] Test interface

## CRM.STAGE.REASON

- [x] Definir modelo en Python.
- [x] Definir vistas Tree, Form.
- [x] Relación Many2many crm.case.stage (n)<---------->(m) crm.stage.reason.

## CRM.CASE.STAGE

- [x] Extender modelo en Python.
- [x] Extender vista Form.
- [x] Relación Many2many crm.case.stage (n)<---------->(m) crm.stage.reason.
- [x] Agregar campo razón por defecto.
- [x] Dominio que restrinja las razones por defecto disponibles a las vinculadas.
- [-] ``_sql_constraint`` que impida agregar razón por defecto inválida
    - behavior has been added with python

## CRM.LEAD

- [x] Relación Many2one crm.lead (n)---------->(1) crm.stage.reason.
- [x] Dominio en crm.lead que restrinja las razones disponibles según la etapa seleccionada.
- [-] ``_sql_constraint``  que impida agregar razón inválida
    - behavior has been added with python
- [ ] Add reason in lead form view
