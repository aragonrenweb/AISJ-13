from odoo import models, fields, api, exceptions, _
from ..utils import formatting

status_types = [
    ("stage", "Stage"),
    ("done", "Done"),
    ("return", "Return To Parents"),
    ("started", "Reenrollment Started"),
    ("submitted", "Submitted"),
    ("cancelled", "Cancelled")
]

class ReenrollmentStatus(models.Model):
    _name = "adm.reenrollment.status"
    _order = "sequence"

    name = fields.Char(string="Status Name")
    description = fields.Text(string="Description")
    sequence = fields.Integer(readonly=True, default=-1)
    fold = fields.Boolean(string="Fold")
    type_id = fields.Selection(status_types, string="Type", default='stage')

    partner_id = fields.Many2one("res.partner", string="Customer", domain=[('next_student_status','like', 'Enrolled')])

    task_ids = fields.One2many("adm.reenrollment.task", "status_id", "Status Ids")

    @api.model
    def create(self, values):
        next_order = self.env['ir.sequence'].next_by_code('sequence.application.task')

        values['sequence'] = next_order
        return super().create(values)


class Gender(models.Model):
    _name = "adm.gender"

    name = fields.Char("Gender")

class Reenrollment(models.Model):
    _name = 'adm.reenrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _read_group_status_ids(self, stages, domain, order):
        status_ids = self.env['adm.reenrollment.status'].search([])
        return status_ids

    # Admission Information
    preferred_degree_program = fields.Many2one("adm.degree_program",
                                               string="Preferred Degree Program")

    # Demographic
    name = fields.Char(string="Name", related="partner_id.name")

    #type_id = fields.Selection(SELECT_REENROLLMENT_STATUS, string="Type", default='stage')


    # Institutional Fee Declaration
    # ===================================================================================================================
    # fee_paid_by_employeer = fields.Boolean()
    # fee_company_name = fields.Char()
    # fee_company_send_invoice = fields.Char()
    # fee_email = fields.Char()
    # fee_signature = fields.Boolean()
    # ===================================================================================================================

    # Meta
    contact_time_id = fields.Many2one("adm.contact_time",
                                      string="Preferred contact time")

    partner_id = fields.Many2one("res.partner", string="Contact")

    first_name = fields.Char(string="Name", related="partner_id.name", required=True) 
    status_id = fields.Many2one("adm.reenrollment.status",
                                string="Status", group_expand="_read_group_status_ids")
    task_ids = fields.Many2many("adm.reenrollment.task")

    state_tasks = fields.One2many(string="State task", related="status_id.task_ids")

    status_type = fields.Selection(string="Status Type", related="status_id.type_id")
    forcing = False

    family_id = fields.Many2one(string="Family", related="partner_id.parent_id")

    def import_student_from_contacts(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/adm.report_default/' + str(self.id),
            'target': '_blank',
            'res_id': self.id,
        }

    def message_get_suggested_recipients(self):
        recipients = super().message_get_suggested_recipients()
        try:
            for inquiry in self:
                if inquiry.email:
                    inquiry._message_add_suggested_recipient(recipients, partner=self.partner_id, email=inquiry.email,
                                                             reason=_('Custom Email Luis'))
        except exceptions.AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def force_back(self):
        status_ids_ordered = self.env['adm.reenrollment.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index -= 1
        if index >= 0:
            next_status = status_ids_ordered[index]
            self.with_context({'forcing': True}).status_id = next_status

    def force_next(self):
        status_ids_ordered = self.env['adm.reenrollment.status'].sudo().search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]
            self.with_context({'forcing': True}).status_id = next_status

    def force_status_submitted(self, next_status_id):
        self.with_context({'forcing': True}).status_id = next_status_id

    def move_to_next_status(self):
        self.forcing = False
        status_ids_ordered = self.env['adm.reenrollment.status'].search([], order="sequence")
        index = 0
        for status in status_ids_ordered:
            if status == self.status_id:
                # print("Encontrado! -> {}".format(index))
                break
            index += 1

        index += 1
        if index < len(status_ids_ordered):
            next_status = status_ids_ordered[index]

            if self.status_id.type_id == 'done':
                raise exceptions.except_orm(_('Application completed'), _('The Application is already done'))
            elif self.status_id.type_id == 'cancelled':
                raise exceptions.except_orm(_('Application cancelled'), _('The Application cancelled'))
            else:
                self.status_id = next_status

    def cancel(self):
        status_ids_ordered = self.env['adm.reenrollment.status'].search([], order="sequence")
        for status in status_ids_ordered:
            if status.type_id == 'cancelled':
                self.status_id = status
                break

    @api.depends("first_name", "middle_name", "last_name")
    def _compute_name(self):
        for record in self:
            record.name = formatting.format_name(record.first_name, record.middle_name, record.last_name)

    # @api.onchange("first_name", "middle_name", "last_name")
    # def _set_full_name(self):
        #self.name = formatting.format_name(self.first_name, self.middle_name, self.last_name)

    @api.onchange("country_id")
    def _onchange_country_id(self):
        res = {}
        if self.country_id:
            res['domain'] = {'state_id': [('country_id', '=', self.country_id.id)]}

    @api.model
    def create(self, values):
        first_status = self.env['adm.reenrollment.status'].search([], order="sequence")[0]
        values['status_id'] = first_status.id
        # values['name'] = formatting.format_name(values['first_name'], values['middle_name'], values['last_name'])

        return super(Reenrollment, self).create(values)

    def write(self, values):

        status_ids = self.env['adm.reenrollment.status'].sudo().search([])

        # first_name = values["first_name"] if "first_name" in values else self.first_name
        # middle_name = values["middle_name"] if "middle_name" in values else self.middle_name
        # last_name = values["last_name"] if "last_name" in values else self.last_name
        #
        # partner_related_fields = dict()
        # partner_related_fields["name"] = values["name"] = formatting.format_name(first_name, middle_name, last_name)

        # "related" in self.fields_get()["email"]
        # Se puede hacer totalmente dinamico, no lo hago ahora por falta de tiempo
        # Pero sin embargo, es totalmente posible.
        # Los no related directamente no tiene related, y los que si son
        # tiene el campo related de la siguiente manera: (model, field)
        # fields = self.fields_get()

        # if "email" in values:
        #     partner_related_fields["email"] = values["email"]
        # if "phone" in values:
        #     partner_related_fields["mobile"] = values["phone"]
        # if "home_phone" in values:
        #     partner_related_fields["phone"] = values["home_phone"]
        # if "country_id" in values:
        #     partner_related_fields["country_id"] = values["country_id"]
        # if "state_id" in values:
        #     partner_related_fields["state_id"] = values["state_id"]
        # if "city" in values:
        #     partner_related_fields["city"] = values["city"]
        # if "street" in values:
        #     partner_related_fields["street"] = values["street"]
        # if "zip" in values:
        #     partner_related_fields["zip"] = values["zip"]
        # if "date_of_birth" in values:
        #     partner_related_fields["date_of_birth"] = values["date_of_birth"]
        #
        # self.sudo().partner_id.write(partner_related_fields)

        print(status_ids)
        #         PARA PONER VALOR POR DEFECTO
        #         self._context.get('forcing', False):
        if "status_id" in values and not self._context.get('forcing', False):
            if not self.state_tasks & self.task_ids == self.state_tasks and self:
                raise exceptions.ValidationError("All task are not completed")
        else:
            self.forcing = False

        return super().write(values)


class ApplicationOtherContacts(models.Model):
    _name = "adm.reenrollment.other_contacts"

    contact_name = fields.Char("Contact Name")
    contact_identification = fields.Char("Contact Identification")

    application_id = fields.Many2one("adm.reenrollment", string="Application")


class ApplicationTasks(models.Model):
    _name = "adm.reenrollment.task"

    name = fields.Char("Name")
    description = fields.Char("Description")
    status_id = fields.Many2one("adm.reenrollment.status", string="Status")


class AdmissionApplicationLanguages(models.Model):
    _name = "adm.reenrollment.language"

    language_id = fields.Many2one("adm.language", string="Language")
    language_level_id = fields.Many2one("adm.language.level", string="Language Level")
    application_id = fields.Many2one("adm.reenrollment", string="Application")
