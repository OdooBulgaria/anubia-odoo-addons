## CRM.STAGE.REASON

- [ ] Definir modelo en Python.
- [ ] Definir vistas Tree, Form.
- [ ] Relación Many2many crm.case.stage (n)<---------->(m) crm.stage.reason.

## CRM.CASE.STAGE

- [ ] Extender modelo en Python.
- [ ] Extender vista Form.
- [ ] Relación Many2many crm.case.stage (n)<---------->(m) crm.stage.reason.
- [ ] Agregar campo razón por defecto.
- [ ] Dominio que restrinja las razones por defecto disponibles a las vinculadas.
- [ ] ``_sql_constraint`` que impida agregar razón por defecto inválida

## CRM.LEAD

- [ ] Relación One2many crm.lead (n)---------->(1) crm.stage.reason.
- [ ] Dominio en crm.lead que restrinja las razones disponibles según la etapa seleccionada.
- [ ] ``_sql_constraint``  que impida agregar razón inválida