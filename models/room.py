from odoo import models, fields, api


class Room(models.Model):
    _name = 'cs.room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Habitación'

    name = fields.Char(string='Número de Habitación', required=True, tracking=True)
    residence_id = fields.Many2one('cs.residence', string='Residencia', required=True, tracking=True)
    tipo = fields.Selection(
        [
            ('individual', 'Individual'),
            ('doble', 'Doble'),
            ('triple', 'Triple'),
        ],
        string='Tipo de Habitación',
        required=True,
        tracking=True
    )
    planta = fields.Char(string='Planta')
    capacidad = fields.Integer(string='Capacidad', default=1)
    ocupados = fields.Integer(string='Ocupados', compute='_compute_ocupados', store=True)
    disponibles = fields.Integer(string='Disponibles', compute='_compute_disponibles', store=True)
    state = fields.Selection(
        [
            ('disponible', 'Disponible'),
            ('ocupada', 'Ocupada'),
            ('mantenimiento', 'Mantenimiento'),
        ],
        string='Estado',
        default='disponible',
        tracking=True
    )
    active = fields.Boolean(default=True, string='Activa')
    notas = fields.Text(string='Notas')
    
    # Relación con residentes
    resident_ids = fields.One2many('cs.resident', 'room_id', string='Residentes')
    
    @api.depends('resident_ids', 'resident_ids.state')
    def _compute_ocupados(self):
        """Calcula cuántos residentes activos hay en la habitación"""
        for room in self:
            room.ocupados = len(room.resident_ids.filtered(lambda r: r.state == 'activo'))

    @api.depends('capacidad', 'ocupados')
    def _compute_disponibles(self):
        """Calcula cuántos espacios disponibles hay"""
        for room in self:
            room.disponibles = room.capacidad - room.ocupados

    @api.constrains('capacidad')
    def _check_capacidad(self):
        """Verifica que capacidad sea positiva"""
        for room in self:
            if room.capacidad <= 0:
                raise ValueError('La capacidad debe ser mayor a 0')
    
    _order = 'residence_id, name'
