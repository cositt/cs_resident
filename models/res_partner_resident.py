from odoo import _, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    resident_ids = fields.One2many(
        "cs.resident",
        "partner_id",
        string="Residentes vinculados",
    )
    resident_count = fields.Integer(compute="_compute_resident_count")

    def _compute_resident_count(self):
        for partner in self:
            partner.resident_count = len(partner.resident_ids)

    def action_create_or_open_resident(self):
        self.ensure_one()
        if self.resident_ids:
            return {
                "type": "ir.actions.act_window",
                "name": _("Residente"),
                "res_model": "cs.resident",
                "res_id": self.resident_ids[0].id,
                "view_mode": "form",
                "target": "current",
            }
        if not self.vat and not self.ref:
            raise UserError(
                _("Indique DNI/NIF (campo NIF/VAT) en el contacto antes de crear el residente.")
            )
        resident = self.env["cs.resident"].create({
            "name": self.name,
            "dni": self.vat or self.ref,
            "phone": self.phone or "",
            "partner_id": self.id,
            "fecha_nacimiento": fields.Date.context_today(self),
        })
        return {
            "type": "ir.actions.act_window",
            "name": _("Residente"),
            "res_model": "cs.resident",
            "res_id": resident.id,
            "view_mode": "form",
            "target": "current",
        }
