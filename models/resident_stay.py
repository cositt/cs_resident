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
    residence_id = fields.Many2one('cs.residence', string='Residencia')
    room_id = fields.Many2one('cs.room', string='Habitación')
    tipo = fields.Selection(
        [
            ('hotel', 'Hotel'),
            ('piso', 'Piso'),
            ('consulta_online', 'Consulta Online'),
            ('otro', 'Otro'),
        ],
        string='Modalidad',
    )
    fecha_inicio = fields.Date(string='Fecha Inicio', required=True, default=fields.Date.context_today)
    fecha_fin = fields.Date(string='Fecha Fin')
    notas = fields.Text(string='Notas')
    dias = fields.Integer(string='Días', compute='_compute_dias')

    @api.depends('fecha_inicio', 'fecha_fin')
    def _compute_dias(self):
        hoy = fields.Date.context_today(self)
        for stay in self:
            fin = stay.fecha_fin or hoy
            stay.dias = (fin - stay.fecha_inicio).days if stay.fecha_inicio else 0

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
                ('fecha_inicio', '<=', stay.fecha_inicio),
            ])
            for prev in previous_open:
                if stay.fecha_inicio > prev.fecha_inicio:
                    prev.fecha_fin = stay.fecha_inicio - timedelta(days=1)
                else:
                    prev.fecha_fin = stay.fecha_inicio
        return stays

    @api.model
    def _backfill_missing_history(self):
        """Reconstruye cs.resident.stay para residentes sin historial usando el
        tracking del chatter de room_id (mail.tracking.value), en vez de dejarlos
        sin registros porque su habitación se asignó antes de que este modelo existiera."""
        residentes = self.env['cs.resident'].search([('stay_ids', '=', False)])
        for residente in residentes:
            self._backfill_resident(residente)

    @api.model
    def _backfill_resident(self, residente):
        tracking_values = self.env['mail.tracking.value'].search([
            ('mail_message_id.model', '=', 'cs.resident'),
            ('mail_message_id.res_id', '=', residente.id),
            ('field_id.name', '=', 'room_id'),
        ], order='create_date asc')

        segmentos = []
        if tracking_values:
            primero = tracking_values[0]
            if primero.old_value_integer:
                segmentos.append((
                    primero.old_value_integer,
                    residente.create_date.date(),
                    primero.create_date.date(),
                ))
            for indice, tracking in enumerate(tracking_values):
                if not tracking.new_value_integer:
                    continue
                siguiente = tracking_values[indice + 1] if indice + 1 < len(tracking_values) else None
                segmentos.append((
                    tracking.new_value_integer,
                    tracking.create_date.date(),
                    siguiente.create_date.date() if siguiente else False,
                ))
        elif residente.room_id:
            segmentos.append((residente.room_id.id, residente.create_date.date(), False))

        rooms = self.env['cs.room']
        for room_id, fecha_inicio, fecha_fin in segmentos:
            room = rooms.browse(room_id)
            if not room.exists():
                continue
            vals = {
                'resident_id': residente.id,
                'room_id': room.id,
                'residence_id': room.residence_id.id,
                'fecha_inicio': fecha_inicio,
            }
            if fecha_fin:
                vals['fecha_fin'] = fecha_fin
            self.create(vals)
