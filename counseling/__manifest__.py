# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Counselor Management',
    'version': '11.0.2.0.0',
    'category': 'Report',
    'description': '''
        Manage appointment on Counselor
        ''',
    'summary': 'Counselor',
    'author': 'Micronaet S.r.l. - Nicola Riolini',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        #'basic_hms',
        #'calendar',
        'xlsxwriter_report',
        'mail',
        ],
    'data': [
        'security/ir.model.access.csv',

        'views/counseling_view.xml',
        #'wizard/export_intervent_wizard.xml',
        ],
    'external_dependencies': {},
    'application': True,
    'installable': True,
    'auto_install': False,
}
