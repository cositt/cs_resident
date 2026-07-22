from datetime import date

from odoo import fields
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
        cls.residencia = cls.env['cs.residence'].create({
            'name': 'Residencia Test',
            'code': 'RES-TEST',
        })
        cls.habitacion_101 = cls.env['cs.room'].create({
            'name': '101',
            'residence_id': cls.residencia.id,
            'tipo': 'individual',
        })
        cls.habitacion_102 = cls.env['cs.room'].create({
            'name': '102',
            'residence_id': cls.residencia.id,
            'tipo': 'individual',
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

    def test_dias_computed_from_fecha_inicio_and_fecha_fin(self):
        stay = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
            'fecha_fin': date(2026, 5, 15),
        })
        self.assertEqual(stay.dias, 5)

    def test_dias_computed_up_to_today_when_open(self):
        stay = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
        })
        hoy = fields.Date.context_today(stay)
        self.assertEqual(stay.dias, (hoy - date(2026, 5, 10)).days)

    def test_creating_resident_with_room_logs_initial_stay(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Con Habitación',
            'dni': '88888888Y',
            'fecha_nacimiento': '1970-01-01',
            'residence_id': self.residencia.id,
            'room_id': self.habitacion_101.id,
        })
        self.assertEqual(len(residente.stay_ids), 1)
        self.assertEqual(residente.stay_ids.room_id, self.habitacion_101)
        self.assertEqual(residente.stay_ids.residence_id, self.residencia)
        self.assertFalse(residente.stay_ids.fecha_fin)

    def test_changing_room_closes_previous_and_opens_new_stay(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Cambia Habitación',
            'dni': '77777777X',
            'fecha_nacimiento': '1970-01-01',
            'residence_id': self.residencia.id,
            'room_id': self.habitacion_101.id,
        })
        primer_stay = residente.stay_ids

        residente.write({'room_id': self.habitacion_102.id})

        self.assertEqual(len(residente.stay_ids), 2)
        self.assertTrue(primer_stay.fecha_fin)
        nuevo_stay = residente.stay_ids - primer_stay
        self.assertEqual(nuevo_stay.room_id, self.habitacion_102)
        self.assertFalse(nuevo_stay.fecha_fin)

    def test_clearing_room_closes_open_stay_without_new_one(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Sale De Habitación',
            'dni': '66666666W',
            'fecha_nacimiento': '1970-01-01',
            'residence_id': self.residencia.id,
            'room_id': self.habitacion_101.id,
        })

        residente.write({'room_id': False})

        self.assertEqual(len(residente.stay_ids), 1)
        self.assertTrue(residente.stay_ids.fecha_fin)

    def test_same_day_stay_closes_previous_same_day(self):
        first = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'hotel',
            'fecha_inicio': date(2026, 5, 10),
        })
        second = self.env['cs.resident.stay'].create({
            'resident_id': self.resident.id,
            'tipo': 'piso',
            'fecha_inicio': date(2026, 5, 10),
        })
        self.assertEqual(first.fecha_fin, date(2026, 5, 10))
        self.assertFalse(second.fecha_fin)

    def test_write_without_room_change_does_not_create_stay(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Sin Cambios',
            'dni': '55555555V',
            'fecha_nacimiento': '1970-01-01',
            'residence_id': self.residencia.id,
            'room_id': self.habitacion_101.id,
        })

        residente.write({'notas': 'Actualización sin relación con habitación'})

        self.assertEqual(len(residente.stay_ids), 1)

    def test_backfill_reconstructs_history_from_chatter_tracking(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Historial Legacy',
            'dni': '44444444U',
            'fecha_nacimiento': '1970-01-01',
        })
        residente.write({'residence_id': self.residencia.id, 'room_id': self.habitacion_101.id})
        self.env.cr.flush()  # simula que el primer cambio quedó guardado como una acción real separada
        residente.write({'room_id': self.habitacion_102.id})
        self.env.cr.flush()

        # Simula un residente "legacy": el chatter ya tiene el tracking real de sus
        # cambios de habitación, pero nunca se le generó cs.resident.stay porque
        # el feature no existía cuando se hicieron esos cambios.
        residente.stay_ids.unlink()
        self.assertFalse(residente.stay_ids)

        self.env['cs.resident.stay']._backfill_missing_history()

        stays = residente.stay_ids.sorted('id')
        self.assertEqual(len(stays), 2)
        self.assertEqual(stays[0].room_id, self.habitacion_101)
        self.assertTrue(stays[0].fecha_fin)
        self.assertEqual(stays[1].room_id, self.habitacion_102)
        self.assertFalse(stays[1].fecha_fin)

    def test_backfill_skips_residents_that_already_have_history(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Con Historial',
            'dni': '33333333T',
            'fecha_nacimiento': '1970-01-01',
            'residence_id': self.residencia.id,
            'room_id': self.habitacion_101.id,
        })
        self.assertEqual(len(residente.stay_ids), 1)

        self.env['cs.resident.stay']._backfill_missing_history()

        self.assertEqual(len(residente.stay_ids), 1)

    def test_backfill_uses_current_room_when_no_tracking_exists(self):
        residente = self.env['cs.resident'].create({
            'name': 'Residente Sin Tracking',
            'dni': '22222222S',
            'fecha_nacimiento': '1970-01-01',
        })
        # Asigna la habitación sin pasar por write() (sin generar tracking),
        # simulando datos importados directamente en la base de datos.
        residente.env.cr.execute(
            "UPDATE cs_resident SET room_id = %s, residence_id = %s WHERE id = %s",
            (self.habitacion_101.id, self.residencia.id, residente.id),
        )
        residente.invalidate_recordset(['room_id', 'residence_id'])
        self.assertFalse(residente.stay_ids)

        self.env['cs.resident.stay']._backfill_missing_history()

        self.assertEqual(len(residente.stay_ids), 1)
        self.assertEqual(residente.stay_ids.room_id, self.habitacion_101)
        self.assertFalse(residente.stay_ids.fecha_fin)
