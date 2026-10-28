from odoo import api, fields, models

ROLES = [
    ('avalista', 'Avalista'),
    ('representante_legal', 'Representante legal'),
    ('persona_apoyo', 'Persona de apoyo'),
    ('contacto_clinico', 'Contacto clínico'),
    ('contacto_economico', 'Contacto económico'),
    ('titular_cuenta', 'Titular de la cuenta'),
]


def _strip_iban(vals):
    if vals.get('iban'):
        return dict(vals, iban=vals['iban'].strip())
    return vals


class ResidentContact(models.Model):
    _name = 'cs.resident.contact'
    _description = 'Persona vinculada al residente (contrato)'
    _order = 'resident_id, sequence, id'

    resident_id = fields.Many2one(
        'cs.resident', string='Residente', required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer(default=10)
    role = fields.Selection(ROLES, string='Rol', required=True)
    name = fields.Char(string='Nombre y apellidos', required=True)
    dni = fields.Char(string='DNI/NIE')
    relationship = fields.Char(string='Parentesco / relación / condición')
    street = fields.Char(string='Dirección')
    city = fields.Char(string='Localidad')
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    iban = fields.Char(string='IBAN')

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([_strip_iban(vals) for vals in vals_list])

    def write(self, vals):
        return super().write(_strip_iban(vals))
