from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Residence(models.Model):
    _name = 'cs.residence'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Residencia'

    name = fields.Char(string='Nombre de Residencia', required=True, tracking=True)
    code = fields.Char(string='Código', required=True, tracking=True)
    direccion = fields.Char(string='Dirección')
    ciudad = fields.Char(string='Ciudad')
    codigo_postal = fields.Char(string='Código Postal')
    provincia = fields.Char(string='Provincia')
    pais = fields.Char(string='País')
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    capacidad_total = fields.Integer(string='Capacidad Total')
    state = fields.Selection(
        [
            ('activa', 'Activa'),
            ('inactiva', 'Inactiva'),
            ('mantenimiento', 'Mantenimiento'),
            ('cerrada', 'Cerrada'),
        ],
        string='Estado',
        default='activa',
        tracking=True
    )
    notas = fields.Text(string='Notas')

    attachment_count = fields.Integer(
        string='Nº archivos vinculados',
        compute='_compute_attachment_count',
    )

    # Relación con habitaciones
    room_ids = fields.One2many('cs.room', 'residence_id', string='Habitaciones')

    _order = 'name'

    @api.depends('message_ids')
    def _compute_attachment_count(self):
        Attachment = self.env['ir.attachment'].sudo()
        for rec in self:
            if not rec.id:
                rec.attachment_count = 0
                continue
            rec.attachment_count = Attachment.search_count(
                [('res_model', '=', 'cs.residence'), ('res_id', '=', rec.id)]
            )

    def action_open_residence_attachments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Planos y documentación'),
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('res_model', '=', 'cs.residence'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'cs.residence',
                'default_res_id': self.id,
            },
            'target': 'current',
        }

    @api.constrains('code')
    def _check_residence_code_unique(self):
        for rec in self:
            dup = self.search_count([('code', '=', rec.code), ('id', '!=', rec.id)])
            if dup:
                raise ValidationError(_('El código de residencia debe ser único.'))
