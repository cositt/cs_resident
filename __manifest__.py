{
    'name': 'Centro Sanitario - Residentes',
    'version': '1.0.0',
    'category': 'Healthcare',
    'author': 'Equilibrium',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'cs_purse_pocket'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/residence_views.xml',
        'views/room_views.xml',
    ],
    'installable': True,
    'application': True,
}
