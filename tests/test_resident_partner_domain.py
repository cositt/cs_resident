from lxml import etree

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


@tagged('post_install', '-at_install')
class TestResidentPartnerDomain(TransactionCase):
    """Residentes → Nuevo debe dejar elegir cualquier contacto persona, no solo los etiquetados Paciente."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env['res.partner']
        cls.contacto_sin_etiqueta = Partner.create({'name': 'Contacto Importado Sin Etiqueta'})
        cls.empresa = Partner.create({'name': 'Empresa Proveedora Test', 'is_company': True})
        cls.ya_residente = Partner.create({'name': 'Contacto Ya Residente'})
        cls.env['cs.resident'].create({
            'name': 'Contacto Ya Residente',
            'dni': '55555555K',
            'fecha_nacimiento': '1970-01-01',
            'partner_id': cls.ya_residente.id,
        })

    def _selectable_partners(self):
        arch = self.env['cs.resident'].get_views([(False, 'form')])['views']['form']['arch']
        field = etree.fromstring(arch).xpath("//field[@name='partner_id']")[0]
        domain = safe_eval(field.get('domain') or '[]')
        return self.env['res.partner'].search(domain)

    def test_contacto_sin_etiqueta_paciente_es_seleccionable(self):
        self.assertIn(self.contacto_sin_etiqueta, self._selectable_partners())

    def test_empresas_no_son_seleccionables(self):
        self.assertNotIn(self.empresa, self._selectable_partners())

    def test_contacto_que_ya_es_residente_no_es_seleccionable(self):
        self.assertNotIn(self.ya_residente, self._selectable_partners())

    def test_al_elegir_contacto_recibe_etiqueta_paciente(self):
        resident = self.env['cs.resident'].new({'partner_id': self.contacto_sin_etiqueta.id})
        resident._onchange_partner_id()
        self.assertIn('Paciente', self.contacto_sin_etiqueta.category_id.mapped('name'))
