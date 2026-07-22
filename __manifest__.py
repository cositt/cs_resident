{
    'name': 'Centro Sanitario - Residentes',
    'version': '1.0.11',
    'category': 'Healthcare',
    'author': 'Equilibrium',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'cs_purse_pocket'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/residence_views.xml',
        'views/room_views.xml',
        'views/resident_stay_views.xml',
        'views/worker_views.xml',
        'views/res_partner_resident_views.xml',
    ],
    'installable': True,
    'application': True,
}
