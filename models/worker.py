from odoo import models, fields, api


class Worker(models.Model):
    _name = 'cs.worker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Trabajador/Profesional'

    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto del Trabajador',
        required=True,
        tracking=True,
        help='Contacto vinculado como trabajador'
    )
    
    name = fields.Char(string='Nombre Completo', related='partner_id.name', store=True)
    phone = fields.Char(string='Teléfono', related='partner_id.phone', store=True)
    email = fields.Char(string='Email', related='partner_id.email', store=True)
    
    job_title = fields.Selection(
        [
            ('psicólogo', 'Psicólogo/a'),
            ('enfermero', 'Enfermero/a'),
            ('médico', 'Médico'),
            ('fisioterapeuta', 'Fisioterapeuta'),
            ('terapeuta', 'Terapeuta'),
            ('cuidador', 'Cuidador/a'),
            ('cocinero', 'Cocinero/a'),
            ('limpiador', 'Limpiador/a'),
            ('administrativo', 'Administrativo/a'),
            ('director', 'Director/a'),
            ('otro', 'Otro'),
        ],
        string='Puesto de Trabajo',
        required=True,
        tracking=True
    )
    
    otro_puesto = fields.Char(
        string='Especificar otro puesto',
        help='Si selecciona "Otro", especifique el puesto aquí'
    )
    
    # UBICACIÓN Y ASIGNACIONES
    residence_ids = fields.Many2many(
        'cs.residence',
        'cs_worker_residence_rel',
        'worker_id',
        'residence_id',
        string='Residencias',
        tracking=True,
        help='Residencias donde trabaja este profesional'
    )
    
    resident_ids = fields.Many2many(
        'cs.resident',
        'cs_worker_resident_rel',
        'worker_id',
        'resident_id',
        string='Residentes Asignados',
        tracking=True,
        help='Residentes bajo el cuidado de este profesional'
    )
    
    # ESTADO
    state = fields.Selection(
        [
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('baja', 'Baja'),
        ],
        string='Estado',
        default='activo',
        tracking=True
    )
    
    notas = fields.Text(string='Notas')
    
    _order = 'name'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-rellenar job_title basado en categorías del partner"""
        if self.partner_id:
            # Mapeo de palabras clave a job_title
            keyword_job_map = {
                'psic': 'psicólogo',
                'enferm': 'enfermero',
                'médic': 'médico',
                'doctor': 'médico',
                'fisio': 'fisioterapeuta',
                'terapeuta': 'terapeuta',
                'cuidador': 'cuidador',
                'cuidadora': 'cuidador',
                'cocinero': 'cocinero',
                'cocinera': 'cocinero',
                'limpiador': 'limpiador',
                'limpiadora': 'limpiador',
                'administ': 'administrativo',
                'director': 'director',
                'directora': 'director',
            }
            
            # Buscar categorías del partner que coincidan
            found = False
            for category in self.partner_id.category_id:
                category_name = category.name.lower().strip()
                # Buscar por palabra clave
                for keyword, job in keyword_job_map.items():
                    if keyword in category_name:
                        self.job_title = job
                        found = True
                        break
                if found:
                    break

    @api.onchange('job_title')
    def _onchange_job_title(self):
        """Limpiar otro_puesto si cambia el puesto seleccionado"""
        if self.job_title != 'otro':
            self.otro_puesto = False
