from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResidentStay(models.Model):
    _name = 'cs.resident.stay'
    _description = 'Periodo de Tratamiento'
    _order = 'fecha_inicio desc, id desc'

    resident_id = fields.Many2one(
        'cs.resident',
        string='Residente',
        required=True,
        ondelete='cascade',
    )
    tipo = fields.Selection(
        [
            ('hotel', 'Hotel'),
            ('piso', 'Piso'),
            ('consulta_online', 'Consulta Online'),
            ('otro', 'Otro'),
        ],
        string='Modalidad',
        required=True,
    )
    fecha_inicio = fields.Date(string='Fecha Inicio', required=True, default=fields.Date.context_today)
    fecha_fin = fields.Date(string='Fecha Fin')
    notas = fields.Text(string='Notas')

    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas(self):
        for stay in self:
            if stay.fecha_fin and stay.fecha_fin < stay.fecha_inicio:
                raise ValidationError(_('La fecha de fin no puede ser anterior a la fecha de inicio.'))

    @api.model_create_multi
    def create(self, vals_list):
        stays = super().create(vals_list)
        for stay in stays:
            previous_open = self.search([
                ('resident_id', '=', stay.resident_id.id),
                ('id', '!=', stay.id),
                ('fecha_fin', '=', False),
                ('fecha_inicio', '<', stay.fecha_inicio),
            ])
            for prev in previous_open:
                prev.fecha_fin = stay.fecha_inicio - timedelta(days=1)
        return stays
