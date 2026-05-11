from odoo import models, fields, api


class Resident(models.Model):
    _name = 'cs.resident'
    _inherit = ['mail.thread']
    _description = 'Residente'

    name = fields.Char(string='Nombre', required=True, tracking=True)
    dni = fields.Char(string='DNI', unique=True, tracking=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', tracking=True)
    edad = fields.Integer(string='Edad', compute='_compute_edad')
    
    phone = fields.Char(string='Teléfono')
    state = fields.Selection(
        [('activo', 'Activo'), ('alta', 'Alta'), ('fallecido', 'Fallecido')],
        default='activo', tracking=True
    )
    
    saldo = fields.Float(string='Saldo (€)', default=0.0, tracking=True)
    
    notas = fields.Text(string='Notas')

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        from datetime import datetime
        for r in self:
            if r.fecha_nacimiento:
                hoy = datetime.now().date()
                r.edad = hoy.year - r.fecha_nacimiento.year
            else:
                r.edad = 0
