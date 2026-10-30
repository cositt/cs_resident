from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, new_test_user


class TestResidentArchive(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.resident = cls.env['cs.resident'].create({
            'name': 'Residente Test Archivo',
            'dni': '88888888Y',
            'fecha_nacimiento': '1950-01-01',
        })
        cls.user = new_test_user(cls.env, login='cs_resident_user', groups='base.group_user')
        cls.admin = new_test_user(cls.env, login='cs_resident_admin', groups='base.group_user,base.group_system')

    def test_new_resident_is_active(self):
        self.assertTrue(self.resident.active)

    def test_user_can_archive_and_unarchive(self):
        resident = self.resident.with_user(self.user)
        resident.action_archive()
        self.assertFalse(resident.active)
        self.assertNotIn(self.resident, self.env['cs.resident'].search([('dni', '=', '88888888Y')]))

        resident.action_unarchive()
        self.assertTrue(resident.active)
        self.assertIn(self.resident, self.env['cs.resident'].search([('dni', '=', '88888888Y')]))

    def test_user_cannot_delete(self):
        with self.assertRaises(AccessError):
            self.resident.with_user(self.user).unlink()

    def test_admin_can_delete(self):
        self.resident.with_user(self.admin).unlink()
        self.assertFalse(self.resident.exists())
