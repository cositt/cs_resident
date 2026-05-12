from odoo import models, fields, api
from datetime import datetime


class Resident(models.Model):
    _name = 'cs.resident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Residente'

    # INFORMACIÓN BÁSICA
    name = fields.Char(string='Nombre Completo', required=True, tracking=True)
    dni = fields.Char(string='DNI/NIF', required=True, unique=True, tracking=True)
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento', required=True, tracking=True)
    edad = fields.Integer(string='Edad', compute='_compute_edad', store=False)
    phone = fields.Char(string='Teléfono')
    
    # ESTADO Y SALDO
    state = fields.Selection(
        [
            ('activo', 'Activo'),
            ('pausado', 'Pausado'),
            ('alta', 'Alta'),
            ('fallecido', 'Fallecido')
        ],
        string='Estado',
        default='activo',
        tracking=True
    )
    
    saldo = fields.Float(string='Saldo (€)', default=0.0, tracking=True)
    notas = fields.Text(string='Notas')

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        """Calcula la edad automáticamente"""
        for residente in self:
            if residente.fecha_nacimiento:
                hoy = datetime.now().date()
                residente.edad = hoy.year - residente.fecha_nacimiento.year
                # Ajustar si aún no ha cumplido años este año
                if (hoy.month, hoy.day) < (residente.fecha_nacimiento.month, residente.fecha_nacimiento.day):
                    residente.edad -= 1
            else:
                residente.edad = 0
