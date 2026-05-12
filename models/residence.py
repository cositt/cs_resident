from odoo import models, fields, api


class Residence(models.Model):
    _name = 'cs.residence'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Residencia'

    name = fields.Char(string='Nombre de Residencia', required=True, tracking=True)
    code = fields.Char(string='Código', required=True, unique=True, tracking=True)
    direccion = fields.Char(string='Dirección')
    ciudad = fields.Char(string='Ciudad')
    codigo_postal = fields.Char(string='Código Postal')
    provincia = fields.Char(string='Provincia')
    pais = fields.Char(string='País')
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    capacidad_total = fields.Integer(string='Capacidad Total')
    active = fields.Boolean(default=True, string='Activa')
    notas = fields.Text(string='Notas')
    
    # Relación con habitaciones
    room_ids = fields.One2many('cs.room', 'residence_id', string='Habitaciones')
    
    _order = 'name'
