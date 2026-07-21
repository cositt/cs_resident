from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResidentStay(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.resident = cls.env['cs.resident'].create({
            'name': 'Residente Test Estancia',
            'dni': '99999999Z',
            'fecha_nacimiento': '1960-01-01',
        })

    def test_stay_requires_fecha_fin_after_fecha_inicio(self):
        with self.assertRaises(ValidationError):
            self.env['cs.resident.stay'].create({
                'resident_id': self.resident.id,
                'tipo': 'hotel',
                'fecha_inicio': date(2026, 5, 15),
                'fecha_fin': date(2026, 5, 10),
            })

    def test_new_open_stay_closes_previous_open_stay(self):
        first = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
        })
        self.assertFalse(first.fecha_fin)

        second = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'piso',
            'fecha_inicio': date(2026, 5, 16),
        })

        self.assertEqual(first.fecha_fin, date(2026, 5, 15))
        self.assertFalse(second.fecha_fin)

    def test_stay_with_explicit_fecha_fin_is_not_touched(self):
        first = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
            'fecha_fin': date(2026, 5, 15),
        })
        self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'consulta_online',
            'fecha_inicio': date(2026, 7, 16),
        })
        self.assertEqual(first.fecha_fin, date(2026, 5, 15))

    def test_current_stay_is_most_recent_open_one(self):
        self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
            'fecha_fin': date(2026, 5, 15),
        })
        second = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'piso',
            'fecha_inicio': date(2026, 5, 16),
        })
        self.assertEqual(self.resident.current_stay_id, second)
        self.assertEqual(self.resident.current_stay_tipo, 'piso')

    def test_no_current_stay_when_all_closed(self):
        self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
            'fecha_fin': date(2026, 5, 15),
        })
        self.assertFalse(self.resident.current_stay_id)
