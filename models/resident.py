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
    
    # CONTACTO VINCULADO
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto (Paciente)',
        tracking=True,
        help='Contacto vinculado como paciente'
    )
    
    # UBICACIÓN DEL RESIDENTE
    residence_id = fields.Many2one(
        'cs.residence',
        string='Residencia',
        tracking=True,
        help='Residencia donde se ubica el residente'
    )
    room_id = fields.Many2one(
        'cs.room',
        string='Habitación',
        tracking=True,
        help='Habitación asignada al residente'
    )
    
    # TRABAJADORES ASIGNADOS
    worker_ids = fields.Many2many(
        'cs.worker',
        'cs_worker_resident_rel',
        'resident_id',
        'worker_id',
        string='Trabajadores Asignados',
        tracking=True,
        help='Trabajadores/Profesionales asignados a este residente'
    )
    
    # ESTADO Y SALDO
    state = fields.Selection(
        [
            ('activo', 'Activo'),
            ('pausado', 'Pausado'),
            ('alta', 'Alta'),
            ('baja', 'Baja')
        ],
        string='Estado',
        default='activo',
        tracking=True
    )
    
    # WALLET Y DATOS ECONÓMICOS
    wallet_id = fields.Many2one(
        'patient.wallet.account',
        string='Cartera del Paciente',
        compute='_compute_wallet_id',
        store=False,
        help='Cartera del paciente vinculada'
    )
    tiene_wallet = fields.Boolean(
        string='¿Tiene Cartera?',
        compute='_compute_tiene_wallet',
        store=False
    )
    saldo = fields.Monetary(
        string='Saldo (€)',
        compute='_compute_saldo',
        store=False,
        currency_field='currency_id',
        help='Saldo actual de la cartera'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    notas = fields.Text(string='Notas')

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        """Calcula la edad automáticamente"""
        for residente in self:
            if residente.fecha_nacimiento:
                hoy = datetime.now().date()
                residente.edad = hoy.year - residente.fecha_nacimiento.year
                if (hoy.month, hoy.day) < (residente.fecha_nacimiento.month, residente.fecha_nacimiento.day):
                    residente.edad -= 1
            else:
                residente.edad = 0

    @api.depends('partner_id')
    def _compute_wallet_id(self):
        """Obtiene la cartera del paciente si existe"""
        for residente in self:
            if residente.partner_id:
                wallet = self.env['patient.wallet.account'].search([
                    ('patient_id', '=', residente.partner_id.id),
                    ('active', '=', True)
                ], limit=1)
                residente.wallet_id = wallet.id if wallet else False
            else:
                residente.wallet_id = False

    @api.depends('wallet_id')
    def _compute_tiene_wallet(self):
        """Verifica si el residente tiene wallet"""
        for residente in self:
            residente.tiene_wallet = bool(residente.wallet_id)

    @api.depends('wallet_id')
    def _compute_saldo(self):
        """Obtiene el saldo de la wallet si existe"""
        for residente in self:
            if residente.wallet_id:
                residente.saldo = residente.wallet_id.balance
            else:
                residente.saldo = 0.0

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Al seleccionar un contacto, auto-completa los datos"""
        if self.partner_id:
            self.name = self.partner_id.name
            self.phone = self.partner_id.phone or ''
            # Buscar DNI/NIF en el campo vat (que es el NIF en Odoo)
            if self.partner_id.vat:
                self.dni = self.partner_id.vat
            elif self.partner_id.ref:
                self.dni = self.partner_id.ref
            # Asegurarse que tiene etiqueta Paciente
            category = self.env['res.partner.category'].search([('name', '=', 'Paciente')])
            if not category:
                category = self.env['res.partner.category'].create({'name': 'Paciente'})
            if category not in self.partner_id.category_id:
                self.partner_id.category_id = [(4, category.id)]

    @api.model_create_multi
    def create(self, vals_list):
        """Al crear residente, crea o vincula un contacto con etiqueta Paciente"""
        for vals in vals_list:
            # Si no hay partner_id, crear uno automáticamente
            if not vals.get('partner_id'):
                # Obtener o crear la categoría "Paciente"
                category = self.env['res.partner.category'].search([('name', '=', 'Paciente')])
                if not category:
                    category = self.env['res.partner.category'].create({'name': 'Paciente'})
                
                # Crear contacto con la etiqueta Paciente
                partner = self.env['res.partner'].create({
                    'name': vals.get('name', 'Sin nombre'),
                    'vat': vals.get('dni', ''),  # Usar vat para DNI/NIF
                    'phone': vals.get('phone', ''),
                    'category_id': [(6, 0, [category.id])],  # Asignar categoría Paciente
                })
                vals['partner_id'] = partner.id
        
        return super().create(vals_list)
