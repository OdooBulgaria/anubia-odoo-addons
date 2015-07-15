This project is an Odoo module which contains the "Anubía, Soluciones en la Nube SL" partner information to be added in new Odoo setup projects.

## Struct

Project has a common Odoo module structure; all external data are in XML files instead CSV.

```
│   __openerp__.py                    Module manifest file
│
├───data
│       res_partner.xml               Anubía Soluciones en la Nube SL, partner information.
│       res_users.xml                 Remote support user, it is disabled by default.
├───i18n
│       es.po                         Spanish modul translation
├───security
│       res_groups.xml                Adds support user to the system groups 
├───static
│   ├───description
│   │       icon.png                  Module icon
│   └───src
│       └───img
│               anubia_company.png    Anubía company icon
│               anubia_contact.png    Anubía support user icon
└───views
        ir_module_module.xml          Filter to display only the modules from Anubia
```

## License

This module is licensed under the **[GNU Affero General Public License, version 3](http://www.gnu.org/licenses/agpl-3.0.html)** license and all documentation is released under [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/).
