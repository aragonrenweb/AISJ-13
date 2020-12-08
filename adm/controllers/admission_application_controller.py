# -*- coding: utf-8 -*-
import logging
from odoo import http
from datetime import datetime
import base64
import itertools
import re
import json
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response

_logger = logging.getLogger(__name__)


def get_parameters():
    return request.httprequest.args


def post_parameters():
    return request.httprequest.form


def lookup(s, lookups):
    for pattern, value in lookups:
        if re.search(pattern, s):
            return value


class AdmissionController(http.Controller):

    @staticmethod
    def _get_values_for_selection_fields(model_env, field_name):
        field_selection_type = model_env._fields[field_name]
        return [{
            'name': name,
            'value': value
            } for value, name in field_selection_type.selection]

    @staticmethod
    def compute_view_render_params(application_id):
        application_id = application_id.sudo()

        relationship_types = AdmissionController._get_values_for_selection_fields(request.env['adm.relationship'], 'relationship_type')
        marital_status_types = AdmissionController._get_values_for_selection_fields(request.env['res.partner'], 'marital_status')
        custodial_rights_types = AdmissionController._get_values_for_selection_fields(request.env['adm.relationship'], 'custodial_rights')

        contact_id = AdmissionController.get_partner()
        contact_time_ids = request.env["adm.contact_time"].search([])
        degree_program_ids = request.env["adm.degree_program"].search([])

        gender_ids = request.env['adm.gender'].search([])
        application_status_ids = request.env["adm.application.status"].search([])

        grade_level_ids = request.env['school_base.grade_level'].sudo().search([])
        school_year_ids = request.env['school_base.school_year'].sudo().search([])

        language_ids = http.request.env['adm.language'].search([])
        language_level_ids = request.env['adm.language.level'].search([])

        country_ids = request.env['res.country'].search([])
        state_ids = request.env['res.country.state'].search([])

        return {
            "country_ids": country_ids,
            "state_ids": state_ids,
            'contact_id': contact_id,
            'application_id': application_id,
            'application_status_ids': application_status_ids,
            'language_ids': language_ids.ids,
            'language_level_ids': language_level_ids.ids,
            'student': application_id,
            'contact_time_ids': contact_time_ids,
            "gender_ids": gender_ids,
            'degree_program_ids': degree_program_ids,
            'current_url': request.httprequest.full_path,
            "showPendingInformation": False,
            "pendingData": AdmissionController.getPendingTasks(application_id),
            'grade_level_ids': grade_level_ids,
            'school_year_ids': school_year_ids,
            'relationship_types': relationship_types,
            'marital_status_types': marital_status_types,
            'custodial_rights_types': custodial_rights_types,
            }

    @staticmethod
    def get_partner():
        return request.env.user.partner_id

    @staticmethod
    def _login_redirect(uid, redirect=None):
        return redirect if redirect else '/web'

    @http.route("/admission/logging_from_facts", auth="public", methods=["GET"], website=True)
    def logging_from_facts(self, **params):
        allow_urls = request.env['ir.config_parameter'].sudo().get_param('allow_urls', '')
        admin_pass = request.env['ir.config_parameter'].sudo().get_param('admin_pass', '')
        route = "/"
        if 'parent_email' in params:
            parent_email = params['parent_email']

        if 'parent_email' in locals():
            user = request.env["res.users"].sudo().search([('email', '=ilike', parent_email)])
            if len(user) > 0:
                uid = request.session.authenticate(request.session.db, 'admin', admin_pass)
                request.session.uid = user.id
                request.session.login = parent_email
                request.params['login_success'] = True

                if 'page' in params:
                    route += "admission/" + params['page']

                    if 'family_id' in params:
                        route += "?family_id=" + str(params['family_id'])

        return request.redirect(route)

        # if ('HTTP_ORIGIN' in request.httprequest.headers.environ):  #     origen_url = request.httprequest.headers.environ['HTTP_ORIGIN']  #  # ApplicationEnv = request.env["adm.application"]  #  # application_ids = ApplicationEnv.sudo().search([("family_id", "=", 481)])  #  # response = request.render('adm.template_admission_application_list', {  #     "application_ids": application_ids,  # })  # return response

    @http.route("/admission/applications", auth="public", methods=["GET"], website=True)
    def admission_list_web(self, **params):
        user_partner = self.get_partner()
        ApplicationEnv = request.env["adm.application"]

        # application_ids = ApplicationEnv.search([("family_id", "=", user_contact.parent_id.id)])
        # obtenemos todas las aplicaciones en las cuales el estudiante asociado este relacionado mediante la familia con el user que esta accediendo dede el portal.
        # application_ids = ApplicationEnv.sudo().search([]).filtered(lambda app: any(i in user_contact.get_families().ids for i in app.partner_id.get_families().ids))
        application_ids = ApplicationEnv.sudo().search([('partner_id.family_ids', 'in', user_partner.family_ids.ids)])
        response = request.render('adm.template_admission_application_list', {
            "application_ids": application_ids,
            })
        return response

    # @http.route("/admission/test_logging", auth="public", methods=["GET"], website=True)
    # def test_logging(self, **params):
    #     user_contact = self.get_partner()
    #     ApplicationEnv = request.env["adm.application"]
    #
    #     application_ids = ApplicationEnv.search([("family_id", "=", user_contact.parent_id.id)])
    #
    #     response = request.render('adm.template_admission_application_list', {
    #         "application_ids": application_ids,
    #     })
    #     return response

    @http.route("/admission/applications/create", auth="public", methods=["GET"], website=True, csrf=False)
    def create_get(self, **params):
        ApplicationEnv = http.request.env["adm.application"]
        CountryEnv = http.request.env['res.country']
        GenderEnv = http.request.env['adm.gender']
        LanguageEnv = http.request.env["adm.language"]
        GradeLevelEnv = http.request.env['school_base.grade_level']
        SchoolYearEnv = http.request.env['school_base.school_year']

        countries = CountryEnv.browse(CountryEnv.search([]))
        genders = GenderEnv.browse(GenderEnv.search([]))
        languages = LanguageEnv.browse(LanguageEnv.search([])).ids
        grade_levels = GradeLevelEnv.browse(GradeLevelEnv.search([('active_admissions', '=', True)])).ids
        school_years = SchoolYearEnv.browse(SchoolYearEnv.search([])).ids
        companies = http.request.env['res.company'].sudo().search([('country_id', '!=', False)])

        template = "adm.template_application_create_application"

        return http.request.render(template, {
            "application_id": ApplicationEnv,
            "countries": countries.ids,
            "student_photo": "data:image/png;base64",
            "adm_languages": languages,
            "genders": genders,
            "grade_levels": grade_levels,
            "school_years": school_years,
            "create_mode": True,
            "create_grade_level": params.get("grade_level"),
            "company": companies and companies[0],
            })

    @http.route("/admission/applications/create", auth="public", methods=["POST"], website=True, csrf=False)
    def info_create_post(self, **params):
        PartnerEnv = http.request.env["res.partner"]
        ApplicationEnv = http.request.env["adm.application"]

        field_ids = http.request.env.ref("adm.model_adm_application").sudo().field_id
        fields = [field_id.name for field_id in field_ids]
        keys = params.keys() & fields
        result = {k: params[k] for k in keys}
        field_types = {field_id.name: field_id.ttype for field_id in field_ids}

        sibling_name_list = post_parameters().getlist("sibling_name")
        sibling_age_list = post_parameters().getlist("sibling_age")
        sibling_school_list = post_parameters().getlist("sibling_school")

        many2one_fields = [name for name, value in field_types.items() if value == "many2one"]

        siblings = [(5, 0, 0)]
        for idx in range(len(sibling_name_list)):
            if sibling_name_list[idx] != '' and sibling_age_list[idx] != '' and sibling_school_list[idx] != '':
                siblings.append((0, 0, {
                    'name': sibling_name_list[idx],
                    'age': sibling_age_list[idx],
                    'school': sibling_school_list[idx],
                    }))
        result["sibling_ids"] = siblings

        for key in result.keys():
            if key in many2one_fields:
                result[key] = int(result[key])
                if result[key] == -1:
                    result[key] = False
                    pass

        parent = http.request.env.user.partner_id.sudo()
        family = parent.family_ids and parent.family_ids[0]

        if not family:
            family = PartnerEnv.sudo().create({
                'name': 'Family of %s' % parent.name,
                'is_family': True,
                'is_company': True,
                'member_ids': [(4, parent.id, False)]
                })
            parent.write({
                'family_ids': [(4, family.id, False)]
                })

        partner = PartnerEnv.sudo().create({
            "first_name": result.get("first_name"),
            "middle_name": result.get("middle_name"),
            "last_name": result.get("last_name"),
            "image_1920": params.get("file_upload") and base64.b64encode(params["file_upload"].stream.read()),
            "parent_id": family.id,
            "person_type": "student",
            "family_ids": [(4, family.id, False)],
            })
        family.write({
            'member_ids': [(4, partner.id, False)]
        })
        application = ApplicationEnv.create({
            "first_name": result.get("first_name"),
            "middle_name": result.get("middle_name"),
            "last_name": result.get("last_name"),
            "partner_id": partner.id,
            })
        result["relationship_ids"] = [(0, 0, {
            "partner_2": parent.id
            })]
        application.sudo().write(result)

        return http.request.redirect("/admission/applications/%s" % application.id)

    @http.route("/admission/applications/<model(adm.application):application_id>", auth="public", methods=["GET"], website=True)
    def admission_web(self, application_id):
        response = request.render('adm.template_application_menu_progress', self.compute_view_render_params(application_id))
        return response

    @http.route("/admission/applications/signature/<int:application_id>", auth="public", methods=["POST"], website=True, csrf=False)
    def send_signature(self, **params):

        print("Params: {}".format(params))
        contact_id = self.get_partner()
        application_id = params["application_id"]
        upload_file = params["signature-pad"]

        AttachmentEnv = request.env["ir.attachment"]

        AttachEnv = request.env["ir.attachment"]
        attach_file = AttachEnv.browse(AttachEnv.sudo().search([('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])])).ids

        attach_file = -1
        last_attach_id = AttachEnv.sudo().search([('name', '=', 'signature.png'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        # attach_file = AttachEnv.browse(AttachEnv.sudo().search([('res_model', '=', 'adm.application'),('res_id', '=', params["application_id"])])).ids
        # attach_file = AttachEnv.browse([1027])

        if upload_file:
            if last_attach_id:
                attach_file = AttachEnv.browse(last_attach_id[0].id)
                attach_file.sudo().write({
                    'res_id': application_id,  # 'x_text': str(attach_file),
                    # base64.b64encode(upload_file.read()),
                    'datas': upload_file,
                    })
            else:
                file_id = AttachmentEnv.sudo().create({
                    'name': 'signature.png',  # 'datas_fname': upload_file.filename,
                    'res_name': 'signature.png',
                    'type': 'binary',
                    'res_model': 'adm.application',
                    'res_id': application_id,  # 'x_text': str(attach_file),
                    # base64.b64encode(upload_file.read()),
                    'datas': upload_file,
                    })

        url_redirect = '/admission/applications/{}/electronic-signature'.format(application_id)

        # GUARDAMOS LA URL DE LA FIRMA PARA LUEGO OBTENER LA FIRMA EN EL REPORTE IMPRESO
        result = {
            "signature_attach_url": last_attach_id.website_url
            }
        request.env["adm.application"].browse([application_id]).sudo().write(result)

        return request.redirect(url_redirect)

    @http.route("/admission/applications/message/<int:application_id>", auth="public", methods=["POST"], website=True, csrf=False)
    def send_message(self, **params):

        print("Params: {}".format(params))
        contact_id = self.get_partner()
        application_id = params["application_id"]
        upload_file = params["file_upload"]
        message_body = params["message_body"]
        origin = params["origin"]
        origin_nameFile = params["origin_filename"]

        message_body = message_body.replace("\n", "<br />\n")

        MessageEnv = request.env["mail.message"]
        message_id = MessageEnv.sudo().create({
            'date': datetime.today(),
            'email_from': '"{}" <{}>'.format(contact_id.name, contact_id.email),
            'author_id': contact_id.id,
            'record_name': "",
            "model": "adm.application",
            "res_id": application_id,
            "message_type": "comment",
            "subtype_id": 1,
            "body": "<p>{}</p>".format(message_body),
            })

        AttachmentEnv = request.env["ir.attachment"]

        attach_file = -1
        last_attach_id = AttachmentEnv.sudo().search([('name', '=', str(origin_nameFile)), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                     order="create_date desc", limit=1)
        # attach_file = AttachEnv.browse(AttachEnv.sudo().search([('res_model', '=', 'adm.application'),('res_id', '=', params["application_id"])])).ids
        # attach_file = AttachEnv.browse([1027])
        if upload_file:
            if last_attach_id:
                attach_file = AttachmentEnv.browse(last_attach_id[0].id)
                attach_file.sudo().write({
                    'name': str(origin_nameFile),  # 'datas_fname': upload_file.filename,
                    'res_name': upload_file.filename,
                    'type': 'binary',
                    'res_model': 'adm.application',
                    'res_name': upload_file.filename,
                    'res_id': application_id,
                    'datas': base64.b64encode(upload_file.read()),
                    })
            else:
                file_id = AttachmentEnv.sudo().create({
                    'name': str(origin_nameFile),  # 'datas_fname': upload_file.filename,
                    'res_name': upload_file.filename,
                    'type': 'binary',
                    'res_model': 'adm.application',
                    'res_id': application_id,
                    'datas': base64.b64encode(upload_file.read()),
                    })
        # url_redirect = '/admission/applications/{}/document-upload'.format(application_id)
        url_redirect = ('/admission/applications/{}/document-' + str(origin)).format(application_id)
        return request.redirect(url_redirect)

        # return request.redirect('/admission/applications')

        # ===============================================================================================================  # return "Ok"  # ===============================================================================================================

    @http.route("/admission/applications/<int:application_id>", auth="public", methods=["POST"], website=True, csrf=False)
    def add_admission(self, **params):

        application_id = params["application_id"]
        if "txtMiddleName" not in params:
            params["txtMiddleName"] = ""

        full_name = "{}, {}{}".format(params["txtLastName"], "" if not params["txtMiddleName"] else params["txtMiddleName"] + " ", params["txtFirstName"])

        new_parent_dict = {
            'name': full_name,
            'first_name': params["txtFirstName"],
            'middle_name': params["txtMiddleName"],
            'last_name': params["txtLastName"],
            'salutation': params["txtSalutation"],
            'email': params["txtEmail"],
            'mobile': params["txtCellPhone"],
            'phone': params["txtHomePhone"],
            'street': params["txtStreetAddress"],  # 'country': params["selCountry"],
            'zip': params["txtZip"]
            }

        if params["selState"] != "-1":
            new_parent_dict["state"] = params["selState"]

        partners = request.env['res.partner']
        id_parent = partners.create(new_parent_dict)

        # Create a lead
        print("application_id: {}".format(application_id))

        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        grade_level_list = post_parameters().getlist("selStudentGradeLevel")
        school_year_list = post_parameters().getlist("selStudentSchoolYear")
        current_school_list = post_parameters().getlist("txtStudentCurrentSchool")
        gender_list = post_parameters().getlist("selStudentGender")
        InquiryEnv = request.env["adm.inquiry"]

        for index_student in range(students_total):
            # print("{} -> {}".format(first_name_list, index_student))
            first_name = first_name_list[index_student]
            middle_name = middle_name_list[index_student]
            last_name = last_name_list[index_student]
            birthday = birthday_list[index_student]
            grade_level = grade_level_list[index_student]
            school_year = school_year_list[index_student]
            current_school = current_school_list[index_student]
            gender = gender_list[index_student]

            full_name_student = "{}, {}{}".format(last_name, "" if not middle_name else middle_name + " ", first_name)

            id_student = InquiryEnv.create({
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'gender': self.env.ref('adm.gender_male').id,
                'birthday': birthday,
                'email': params["txtEmail"],
                'school_year': school_year,
                'grade_level': grade_level,
                'current_school': current_school,
                'responsible_id': id_parent.id
                })
            id_students.append(id_student)

        return request.redirect('/admission/applications')

    # adm.previous_school_description
    def set_house_address(self, application_id, params):
        if "has_house_address" in params:

            post_params = post_parameters()
            house_address_ids = post_params.getlist("house_address_id")

            # CONVET STRING LIST TO INT LIST
            house_address_ids = list(map(int, house_address_ids))

            house_address_name = post_params.getlist("house_address_name")
            house_address_country_id = post_params.getlist("house_address_country_id")

            house_address_state_id = ''
            if 'house_address_state_id' in post_params:
                house_address_state_id = post_params.getlist("house_address_state_id")

            house_address_city = post_params.getlist("house_address_city")
            house_address_zip = post_params.getlist("house_address_zip")
            house_address_street = post_params.getlist("house_address_street")
            house_address_phone = post_params.getlist("house_address_phone")

            application = request.env["adm.application"].browse([application_id])

            HouseAddressEnv = request.env["adm.house_address"]

            # First, delete all that are not in the form, that's why the user clicked remove button.
            all_ids = set(application.sudo().partner_id.parent_id.house_address_ids.ids)
            form_ids = {id for id in house_address_ids if id != -1}

            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [(2, id, 0) for id in ids_to_delete]

            if unlink_commands:
                application.sudo().partner_id.parent_id.write({
                    "house_address_ids": unlink_commands
                    })

            # PartnerEnv = request.env["res.partner"]

            # USANDO UN ITERADOR TOMA CADA UNO DE LAS LISTAS EN EL ZIP_LONGEST  Y LO ASIGNA A CADA UNA DE LAS VARIABLES QUE SE ASIGNA EN EL FOR
            for id, name, country_id, state_id, city, zip, street, phone in itertools.zip_longest(house_address_ids, house_address_name, house_address_country_id,
                                                                                                  house_address_state_id, house_address_city, house_address_zip,
                                                                                                  house_address_street, house_address_phone, fillvalue=False):
                if id != -1:
                    partner = HouseAddressEnv.browse([id])
                    partner.sudo().write({
                        "name": name,
                        "country_id": country_id,
                        "state_id": state_id,
                        "city": city,
                        "zip": zip,
                        "street": street,
                        "phone": phone,
                        })
                else:
                    partner = HouseAddressEnv.sudo().create({
                        "name": name,
                        "country_id": country_id,
                        "state_id": state_id,
                        "city": city,
                        "zip": zip,
                        "street": street,
                        "phone": phone,
                        "family_id": application.partner_id.parent_id.id
                        })  # application.sudo().write({"house_address_ids": [(4, partner.sudo().id, 0)]})

                #             SOLO EN EL CASO DE LOS DEL INSTITUTO ALBERT EISNTEIN QUE TENDRAN COMO MÁXIMO UNA DIRECCIÓN PARA LA FAMILIA, cuando se modifique o se añada se cambiará la direccion a todos los contactos asociados a esta familia.
                if state_id:
                    state_id = int(state_id)

                application.sudo().partner_id.parent_id.sudo().write({
                    "country_id": int(country_id),
                    "state_id": state_id,
                    "city": city,
                    "zip": zip,
                    "street": street,
                    })
                for member in application.sudo().partner_id.parent_id.member_ids:
                    member.sudo().write({
                        "country_id": int(country_id),
                        "state_id": state_id,
                        "city": city,
                        "zip": zip,
                        "street": street,
                        })

    def set_medical_info(self, application_id, params):
        if "has_medical_info" in params:

            post_params = post_parameters()

            application = request.env["adm.application"].browse([application_id])

            # -- Conditions -- #
            medical_conditions_ids = post_params.getlist("medical_condition_id")
            medical_allergies_ids = post_params.getlist("medical_allergy_id")
            medical_medications_ids = post_params.getlist("medical_medication_id")

            medical_conditions_ids = list(map(int, medical_conditions_ids))
            medical_allergies_ids = list(map(int, medical_allergies_ids))
            medical_medications_ids = list(map(int, medical_medications_ids))

            medical_condition_name = post_params.getlist("medical_condition_name")
            medical_condition_comment = post_params.getlist("medical_condition_comment")

            medical_allergy_name = post_params.getlist("medical_allergy_name")
            medical_allergy_comment = post_params.getlist("medical_allergy_comment")

            medical_medication_name = post_params.getlist("medical_medication_name")
            medical_medication_comment = post_params.getlist("medical_medication_comment")

            # First, delete all that are not in the form, that's why the user clicked remove button.

            # -- Conditions --#
            all_ids = set(application.sudo().medical_conditions_ids.ids)
            form_ids = {id for id in medical_conditions_ids if id != -1}

            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [(2, id, False) for id in ids_to_delete]

            if unlink_commands:
                application.sudo().write({
                    "medical_conditions_ids": unlink_commands
                    })
            # -------------------

            # -- Allergies --#
            all_ids = set(application.sudo().medical_allergies_ids.ids)
            form_ids = {id for id in medical_allergies_ids if id != -1}

            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [(2, id, False) for id in ids_to_delete]

            if unlink_commands:
                application.sudo().write({
                    "medical_allergies_ids": unlink_commands
                    })
            # -------------------

            # -- Medications --#
            all_ids = set(application.sudo().medical_medications_ids.ids)
            form_ids = {id for id in medical_medications_ids if id != -1}

            ids_to_delete = all_ids ^ form_ids
            unlink_commands = [(2, id, False) for id in ids_to_delete]

            if unlink_commands:
                application.sudo().write({
                    "medical_medications_ids": unlink_commands
                    })
            # -------------------

            # -- Conditions -- #
            conditions_create_commands = list()
            conditions_write_comands = list()

            for id, name, comment in itertools.zip_longest(medical_conditions_ids, medical_condition_name, medical_condition_comment, fillvalue=False):
                if id != -1:
                    conditions_write_comands.append((1, id, {
                        "name": name,
                        "comment": comment
                        }))
                else:
                    conditions_create_commands.append((0, False, {
                        "name": name,
                        "comment": comment
                        }))

            conditions_commands = conditions_create_commands + conditions_write_comands
            # -------------------

            # -- Allergies -- #
            allergies_create_commands = list()
            allergies_write_comands = list()

            for id, name, comment in itertools.zip_longest(medical_allergies_ids, medical_allergy_name, medical_allergy_comment, fillvalue=False):
                if id != -1:
                    allergies_create_commands.append((1, id, {
                        "name": name,
                        "comment": comment
                        }))
                else:
                    allergies_write_comands.append((0, False, {
                        "name": name,
                        "comment": comment
                        }))

            allergies_commands = allergies_write_comands + allergies_create_commands
            # -------------------

            # -- Medications -- #
            medications_create_commands = list()
            medications_write_comands = list()

            for id, name, comment in itertools.zip_longest(medical_medications_ids, medical_medication_name, medical_medication_name, fillvalue=False):
                if id != -1:
                    conditions_write_comands.append((1, id, {
                        "name": name,
                        "comment": comment
                        }))
                else:
                    medications_write_comands.append((0, False, {
                        "name": name,
                        "comment": comment
                        }))

            medications_commands = medications_create_commands + medications_write_comands
            # -------------------

            application.sudo().write({
                "medical_conditions_ids": conditions_commands,
                "medical_allergies_ids": allergies_commands,
                "medical_medications_ids": medications_commands,
                })

    def set_additional_student(self, application_id, params):
        if "is_additional_student_info" in params:
            # post_params = post_parameters()

            # ===========================================================================================================
            # first_language_skills = post_params.getlist("first_language_skills")
            # first_language_skills = list(map(int, first_language_skills))
            # 
            # second_language_skills = post_params.getlist("second_language_skills")
            # second_language_skills = list(map(int, second_language_skills))
            # 
            # third_language_skills = post_params.getlist("third_language_skills")
            # third_language_skills = list(map(int, third_language_skills))
            # 
            # ===========================================================================================================
            application = request.env["adm.application"].browse([application_id])

            application.sudo().write({
                "first_language_skill_write": False,
                "first_language_skill_read": False,
                "first_language_skill_speak": False,
                "first_language_skill_listen": False,

                "second_language_skill_write": False,
                "second_language_skill_read": False,
                "second_language_skill_speak": False,
                "second_language_skill_listen": False,

                "third_language_skill_write": False,
                "third_language_skill_read": False,
                "third_language_skill_speak": False,
                "third_language_skill_listen": False,
                })

    def set_previous_school(self, application_id, params):
        if "has_previous_schools" in params:

            post_params = post_parameters()
            previous_school_ids = post_params.getlist("previous_school_id")
            previous_school_ids = list(map(int, previous_school_ids))

            previous_school_names = post_params.getlist("previous_school_name")
            previous_school_street = post_params.getlist("previous_school_street")
            previous_school_city = post_params.getlist("previous_school_city")
            previous_school_country = post_params.getlist("previous_school_country")
            previous_school_state = post_params.getlist("previous_school_state")
            # previous_school_zip = post_params.getlist("previous_school_zip")
            # previous_school_phone = post_params.getlist("previous_school_phone")
            previous_school_fromdate = post_params.getlist("previous_school_fromdate")
            previous_school_todate = post_params.getlist("previous_school_todate")
            previous_school_gradecompleted = post_params.getlist("previous_school_gradecompleted")
            previous_school_extracurricular_interests = post_params.getlist("previous_school_extracurricular_interests")

            PreviousSchoolDescriptionEnv = request.env["adm.previous_school_description"]
            application = request.env["adm.application"].browse([application_id])

            # First, delete all that are not in the form, that's why the user clicked remove button.
            all_ids = set(application.previous_school_ids.ids)
            form_ids = {id for id in previous_school_ids if id != -1}

            ids_to_delete = all_ids ^ form_ids
            PreviousSchoolDescriptionEnv.browse(ids_to_delete).unlink()

            # for id, name, street, city, state, country, zip, phone, from_date, to_date, grade_completed, extracurricular_interests \
            # in itertools.zip_longest(previous_school_ids, previous_school_names, previous_school_street,
            #                          previous_school_city, previous_school_state, previous_school_country,
            #                          previous_school_zip, previous_school_phone, previous_school_fromdate,
            #                          previous_school_todate, previous_school_gradecompleted,previous_school_extracurricular_interests,
            #                          fillvalue=False):
            for id, name, street, city, state, country, from_date, to_date, grade_completed, extracurricular_interests in itertools.zip_longest(previous_school_ids,
                                                                                                                                                previous_school_names,
                                                                                                                                                previous_school_street,
                                                                                                                                                previous_school_city,
                                                                                                                                                previous_school_state,
                                                                                                                                                previous_school_country,
                                                                                                                                                previous_school_fromdate,
                                                                                                                                                previous_school_todate,
                                                                                                                                                previous_school_gradecompleted,
                                                                                                                                                previous_school_extracurricular_interests,
                                                                                                                                                fillvalue=False):
                if id != -1:
                    PreviousSchoolDescriptionEnv.browse([id]).write({
                        "name": name,
                        "city": city,
                        "country_id": country,
                        "state_id": state,  # "zip": zip,
                        "street": street,  # "phone": phone,
                        "from_date": from_date,
                        "to_date": to_date,
                        "grade_completed": grade_completed,
                        "extracurricular_interests": extracurricular_interests,
                        })
                    pass
                else:
                    PreviousSchoolDescriptionEnv.create({
                        "application_id": application_id,
                        "name": name,
                        "country_id": country,
                        "city": city,
                        "state_id": state,  # "zip": zip,
                        "street": street,  # "phone": phone,
                        "from_date": from_date,
                        "to_date": to_date,
                        "grade_completed": grade_completed,
                        "extracurricular_interests": extracurricular_interests,
                        })
        pass

    def set_contact(self, application_id, params):
        if "has_contact" in params:

            new_profile_photos = []
            profile_photos = []

            for key, value in params.items():  # VOY A OBLIGAR LA FOTO PARA QUE COINCIDA LA CANTIDAD DE FOTOS CON LA DE LAS PERSONS
                if key.startswith('new_file_upload'):
                    new_profile_photos.append(value)

            total_file_upload = 0
            for key, value in params.items():  # VOY A OBLIGAR LA FOTO PARA QUE COINCIDA LA CANTIDAD DE FOTOS CON LA DE LAS PERSONS
                if key.startswith('file_upload'):
                    # total_file_upload = total_file_upload + 1
                    profile_photos.append(value)

            # for cont_file_upload in range(0, total_file_upload):
            #     if 'file_upload_' + str(cont_file_upload) in params:
            #         profile_photos.append(params['file_upload_' + str(cont_file_upload)])

            post_params = post_parameters()
            contact_ids = post_params.getlist("contact_id")
            contact_ids = list(map(int, contact_ids))

            contact_existing_id = post_params.getlist("contact_existing_id")
            contact_existing_id = list(map(int, contact_existing_id))

            new_contact_id = post_params.getlist("new_contact_id")
            new_contact_id = list(map(int, new_contact_id))

            relationship_type = post_params.getlist("relationship_type")
            relation_partner_mobile = post_params.getlist("relation_partner_mobile")
            relation_partner_phone = post_params.getlist("relation_partner_phone")
            relation_partner_email = post_params.getlist("relation_partner_email")
            relationship_house = post_params.getlist("relationship_house")
            relationship_is_emergency_contact = post_params.getlist("relationship_is_emergency_contact")

            # customization current howard academy
            current_partner_citizenship = post_params.getlist("current_partner_nationality")
            current_partner_identification = post_params.getlist("current_partner_identification")
            current_partner_marital_status = post_params.getlist("current_partner_marital_status")
            current_partner_occupation = post_params.getlist("current_partner_occupation")
            current_partner_office_address = post_params.getlist("current_partner_office_address")
            current_partner_office_phone = post_params.getlist("current_partner_office_phone")
            current_partner_title = post_params.getlist("current_title")
            current_partner_other_reason = post_params.getlist("current_other_reason")

            for key, value in post_params.items():  # iter on both keys and values
                if key.startswith('title_radio_'):
                    current_partner_title.append(value)

            current_partner_parental_responsability = post_params.getlist("current_relationship_is_parental_responsability")
            current_partner_fees_payable = post_params.getlist("current_partner_fees_payable")
            current_partner_extra_payable = post_params.getlist("current_partner_extra_payable")

            # From new contacts
            new_partner_name = post_params.getlist("new_partner_name")
            new_partner_first_name = post_params.getlist("new_partner_first_name")
            new_partner_middle_name = post_params.getlist("new_partner_middle_name")
            new_partner_last_name = post_params.getlist("new_partner_last_name")

            new_partner_mobile = post_params.getlist("new_partner_mobile")
            new_partner_phone = post_params.getlist("new_partner_phone")
            new_partner_email = post_params.getlist("new_partner_email")
            new_relationship_type = post_params.getlist("new_relationship_type")
            new_relationship_house = post_params.getlist("new_relationship_house")
            new_relationship_is_emergency_contact = post_params.getlist("new_relationship_is_emergency_contact")

            # customization new howard academy
            new_partner_citizenship = post_params.getlist("new_partner_nationality")
            new_partner_identification = post_params.getlist("new_partner_identification")
            new_partner_marital_status = post_params.getlist("new_partner_marital_status")
            new_partner_occupation = post_params.getlist("new_partner_occupation")
            new_partner_office_address = post_params.getlist("new_partner_office_address")
            new_partner_office_phone = post_params.getlist("new_partner_office_phone")
            new_partner_title = post_params.getlist("title")
            new_partner_other_reason = post_params.getlist("other_reason")

            for key, value in post_params.items():  # iter on both keys and values
                if key != 'title_new_radio_0' and key.startswith('title_new_radio_'):
                    new_partner_title.append(value)

            new_partner_parental_responsability = post_params.getlist("new_relationship_is_parental_responsability")
            new_partner_fees_payable = post_params.getlist("new_partner_fees_payable")
            new_partner_extra_payable = post_params.getlist("new_partner_extra_payable")

            new_partner_photos = post_params.getlist("new_file_upload")

            PartnerEnv = request.env["res.partner"]
            RelationshipEnv = request.env["adm.relationship"]
            application = request.env["adm.application"].browse([application_id])

            # First, delete all that are not in the form, that's why the user clicked remove button.
            ids_to_delete = {relation.id for relation in application.relationship_ids if not relation.partner_2.id in contact_ids}
            unlink_commands = [(2, id, 0) for id in ids_to_delete]

            application.sudo().write({
                "relationship_ids": unlink_commands,
                })

            # Link all existing ids.
            application.sudo().write({
                "relationship_ids": [(0, 0, {
                    "partner_1": application.partner_id.id,
                    "partner_2": id,
                    }) for id in contact_existing_id],
                })
            idx = 0
            for id, type, mobile, phone, email, house_address_id, is_emergency_contact, citizenship, identification, marital_status, occupation, office_address, office_phone, title, other_reason, parental_responsability, fees_payable, extra_payable in itertools.zip_longest(
                    contact_ids, relationship_type, relation_partner_mobile, relation_partner_phone, relation_partner_email, relationship_house, relationship_is_emergency_contact,
                    current_partner_citizenship, current_partner_identification, current_partner_marital_status, current_partner_occupation, current_partner_office_address,
                    current_partner_office_phone, current_partner_title, current_partner_other_reason, current_partner_parental_responsability, current_partner_fees_payable,
                    current_partner_extra_payable, fillvalue=False):

                # SUBIR FOTO DEL PERSON
                # if "file_upload" in params:
                #     upload_file = params["file_upload"]
                #     # image_1920

                if id != -1:
                    if title == 'other':
                        title = other_reason

                    relationship = application.relationship_ids.filtered(lambda relation: relation.partner_2.id == id)
                    relationship.sudo().write({
                        "relationship_type": type,
                        "is_emergency_contact": is_emergency_contact,
                        })

                    partnerData = {
                        "phone": phone,
                        "mobile": mobile,
                        "email": email,
                        "email": email,
                        "house_address_id": house_address_id,
                        "citizenship": citizenship,
                        "identification": identification,
                        "marital_status": marital_status,
                        "occupation": occupation,
                        "work_address": office_address,
                        "work_phone": office_phone,
                        "title": title,
                        "parental_responsability": parental_responsability,
                        }

                    if profile_photos[idx] != '-1':
                        upload_file = profile_photos[idx]
                        partnerData['image_1920'] = base64.b64encode(upload_file.stream.read())

                    PartnerEnv.sudo().browse([id]).write(partnerData)

                    # PartnerEnv.sudo().browse([id]).write({
                    #     "phone": phone,
                    #     "mobile": mobile,
                    #     "email": email,
                    #     "email": email,
                    #     "house_address_id": house_address_id,
                    #     "citizenship": citizenship,
                    #     "identification": identification,
                    #     "marital_status": marital_status,
                    #     "marital_status": marital_status,
                    #     "occupation": occupation,
                    #     "work_address": office_address,
                    #     "work_phone": office_phone,
                    #     "image_1920": base64.b64encode(upload_file.stream.read()),
                    #     "title": title,
                    #     "parental_responsability":parental_responsability,
                    #     "percent_extras_payable":fees_payable,
                    #     "percent_fees_payable":extra_payable,
                    # })
                    idx = idx + 1

            idx = 0
            for name, first_name, middle_name, last_name, mobile, phone, email, type, house_address_id, is_emergency_contact, citizenship, identification, marital_status, occupation, office_address, office_phone, title, other_reason, parental_responsability, fees_payable, extra_payable, partner_photo in itertools.zip_longest(
                    new_partner_name, new_partner_first_name, new_partner_middle_name, new_partner_last_name, new_partner_mobile, new_partner_phone, new_partner_email,
                    new_relationship_type, new_relationship_house, new_relationship_is_emergency_contact, new_partner_citizenship, new_partner_identification,
                    new_partner_marital_status, new_partner_occupation, new_partner_office_address, new_partner_office_phone, new_partner_title, new_partner_other_reason,
                    new_partner_parental_responsability, new_partner_fees_payable, new_partner_extra_payable, new_partner_photos, fillvalue=False):

                if title == 'other':
                    title = other_reason

                partner_aux = {
                    # "name": name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "parent_id": application.partner_id.parent_id.id,
                    "phone": phone,
                    "mobile": mobile,
                    "email": email,
                    "house_address_id": house_address_id,
                    "citizenship": citizenship,
                    "identification": identification,
                    "marital_status": marital_status,
                    "occupation": occupation,
                    "work_address": office_address,
                    "work_phone": office_phone,
                    "image_1920": base64.b64encode(new_profile_photos[idx].stream.read()),
                    "title": title,
                    "parental_responsability": parental_responsability,
                    }

                new_partner = PartnerEnv.sudo().create(partner_aux)

                application.sudo().write({
                    "relationship_ids": [(0, 0, {
                        "partner_2": new_partner.id,
                        "relationship_type": type,
                        "is_emergency_contact": is_emergency_contact,
                        })]
                    })
                idx = idx + 1
        pass

    def parse_json_to_odoo_fields(self, model_env, json_request: dict):
        json_to_build = {}

        for field, value in json_request.items():
            value_to_json = False
            if isinstance(value, list):
                if value:
                    rel_model_env = request.env[model_env._fields[field].comodel_name].sudo()
                    parsed_vals = [(5, 0, 0)]
                    for val_array in value:
                        if 'id' not in val_array or not val_array['id']:
                            parsed_vals.append((0, 0, self.parse_json_to_odoo_fields(rel_model_env, val_array)))
                        else:
                            rel_id = val_array.pop('id')
                            parsed_vals.append((4, rel_id, False))
                            if len(val_array.keys()):
                                rel_model_env.browse(rel_id).write(self.parse_json_to_odoo_fields(rel_model_env, val_array))
                    value_to_json = parsed_vals
            elif isinstance(value, dict):
                model_name = model_env._fields[field].comodel_name
                rel_model_env = request.env[model_name].sudo()

                if 'id' not in value or not value['id']:
                    if len(model_env) == 1 and model_name == 'ir.attachment':
                        attachment_id = model_env.env['ir.attachment'].sudo().create({
                            'name': value['name'],
                            'datas': value['base64_encoded_file'],
                            'mimetype': value['content_type'],
                            'res_id': model_env.id,
                            'res_model': model_env._name,
                            'type': 'binary',
                            })
                        rel_id = attachment_id.id
                    else:
                        rel_id = rel_model_env.create(self.parse_json_to_odoo_fields(rel_model_env, value)).id
                else:
                    rel_id = value.pop('id')

                    for aux_field in value:
                        if hasattr(rel_model_env._fields[aux_field], 'comodel_name'):
                            if rel_model_env._fields[aux_field].comodel_name == 'ir.attachment':
                                attachment_dict = value.pop(aux_field)
                                attachment_id = rel_model_env.env['ir.attachment'].create({
                                    'name': attachment_dict['name'],
                                    'datas': attachment_dict['base64_encoded_file'],
                                    'mimetype': attachment_dict['content_type'],
                                    'res_id': rel_id,
                                    'res_model': model_name,
                                    'type': 'binary',
                                    })
                                value[aux_field] = attachment_id.id

                    if len(value.keys()):
                        rel_model_env.browse(rel_id).write(self.parse_json_to_odoo_fields(rel_model_env, value))
                value_to_json = rel_id
            else:
                if not value:
                    value = False
                value_to_json = value
            json_to_build[field] = value_to_json

        return json_to_build

    @http.route("/admission/applications/<model(adm.application):application_id>/", auth="public", methods=["PUT"], csrf=True, type='json')
    def update_application_with_json(self, application_id, **params):
        """ This is a JSON controller, this get a JSON and write the application with it, that's all """
        json_request = request.jsonrequest
        write_vals = self.parse_json_to_odoo_fields(application_id, json_request)
        application_id.sudo().write(write_vals)

    @http.route("/admission/applications/<model(adm.application):application_id>/avatar", auth="public", methods=["POST"], csrf=True, type='json')
    def upload_partner_avatar(self, application_id, **params):
        """ This is a JSON controller, this get a JSON and write the application with it, that's all """
        json_request = request.jsonrequest
        # decodedFile = base64.b64decode()
        application_id.sudo().partner_id.write({
            'image_1920': json_request['file'].split(',')[1]
            })

    @staticmethod
    def insert_files_into_application_field(application_id, application_field, json_name, json_request):
        if json_name in json_request:
            application_id.sudo().write({
                application_field: [(0, 0, {
                    'name': json_request[json_name]['name'],
                    'datas': json_request[json_name]['file'].split(',')[1],
                    'mimetype': json_request[json_name]['content_type'],
                    'res_id': application_id.id,
                    'res_model': 'adm.application',
                    'type': 'binary',
                    })]
                })

    @http.route("/admission/applications/<model(adm.application):application_id>/student-files", auth="public", methods=["POST"], csrf=True, type='json')
    def submit_student_files(self, application_id, **params):
        """ This is a JSON controller, this get a JSON and write the application with it, that's all """
        json_request = request.jsonrequest

        self.insert_files_into_application_field(application_id, 'passport_file_ids', 'passportFile', json_request)
        self.insert_files_into_application_field(application_id, 'residency_file_ids', 'residencyFile', json_request)

    @http.route("/admission/applications/<int:application_id>/write", auth="public", methods=["POST"], website=True, csrf=False)
    def write_application(self, application_id, **params):
        field_ids = request.env.ref("adm.model_adm_application").sudo().field_id
        fields = [field_id.name for field_id in field_ids]
        keys = params.keys() & fields
        result = {k: params[k] for k in keys}
        field_types = {field_id.name: field_id.ttype for field_id in field_ids}

        sibling_name_list = post_parameters().getlist("sibling_name")
        sibling_age_list = post_parameters().getlist("sibling_age")
        sibling_school_list = post_parameters().getlist("sibling_school")
        # if field_id.ttype != 'one2many' and field_id.ttype != 'many2many'

        self.set_house_address(application_id, params)
        self.set_previous_school(application_id, params)
        self.set_additional_student(application_id, params)
        self.set_contact(application_id, params)
        self.set_medical_info(application_id, params)

        many2one_fields = [name for name, value in field_types.items() if value == "many2one"]

        if 'file_upload' in params and params["file_upload"] is not '' and "has_contact" not in params:
            upload_file = params["file_upload"]
            request.env["res.partner"].sudo().browse([request.env["adm.application"].browse([application_id]).partner_id.id]).write({
                "image_1920": base64.b64encode(upload_file.stream.read())
                })

        # SI LOS CAMPOS BOOLEANOS NO EXISTEN EN LOS PARAMETROS LOS INICIALIZAMOS A FALSE PARA QUE SE DESACTIVEN.

        # DATOS DEL DESARROLLO SOCIAL
        if 'pe_avisa_bano' not in result:
            result["pe_avisa_bano"] = False

        if 'pe_duerme_toda_noche' not in result:
            result["pe_duerme_toda_noche"] = False

        if 'pe_comer_sentado' not in result:
            result["pe_comer_sentado"] = False

        if 'pe_viste_solo' not in result:
            result["pe_viste_solo"] = False

        # HABILIDADES PARA EL APRENDIZAJE Y VIDA ESCOLAR
        if 'pe_se_concentra' not in result:
            result["pe_se_concentra"] = False

        if 'pe_termina_lo_que_comienza' not in result:
            result["pe_termina_lo_que_comienza"] = False

        if 'pe_logra_seguir_indicaciones' not in result:
            result["pe_logra_seguir_indicaciones"] = False

        if 'pe_logra_separarse_padres' not in result:
            result["pe_logra_separarse_padres"] = False

        siblings = [(5, 0, 0)]
        for idx in range(len(sibling_name_list)):
            if sibling_name_list[idx] != '' and sibling_age_list[idx] != '' and sibling_school_list[idx] != '':
                siblings.append((0, 0, {
                    'name': sibling_name_list[idx],
                    'age': sibling_age_list[idx],
                    'school': sibling_school_list[idx],
                    }))
        result["siblings"] = siblings

        # upload_file = params["file_upload"]
        # result['partner_id.image_1920'] = base64.b64encode(upload_file.stream.read())

        for key in result.keys():
            if key in many2one_fields:
                result[key] = int(result[key])
                if result[key] == -1:
                    result[key] = False
                    pass

        # ===============================================================================================================
        # one2many_fields = [name for name, value in field_types.items() if value == "one2many"]
        # many2many_fields = [name for name, value in field_types.items() if value == "many2many"]
        #  
        # for key in post_params.keys():
        #     if key in many2many_fields:
        #         pass
        # ===============================================================================================================

        if result:
            request.env["adm.application"].browse([application_id]).sudo().write(result)

        return request.redirect(http.request.httprequest.referrer)

    @http.route("/admission/applications/<model(adm.application):application_id>/check", auth="public", methods=["POST"], website=True, csrf=False)
    def check_application(self, application_id, **params):

        if len(self.getPendingTasks(application_id)) == 0:
            # BUSCAMOS EL STATUS QUE SEA DE TIPO SUBMITTED PARA TRANSLADAR LA PETICION DEL USUARIO
            StatusEnv = request.env["adm.application.status"].sudo()
            statusSubmitted = StatusEnv.browse(StatusEnv.search([('type_id', '=', 'submitted')]))
            application_id.sudo().force_status_submitted(statusSubmitted.id.id)

        return request.redirect(http.request.httprequest.referrer + "?checkData=1")

    @http.route("/admission/<int:application_id>/check_email", auth="public", methods=["POST"], csrf=False)
    def check_email(self, application_id, **params):
        email_to_check = str(params['email']).strip()
        # ApplicationEnv = request.env["adm.application"]
        PartnerEnv = request.env["res.partner"]
        # ApplicationEnv.browse([application_id]).relationship_ids[1].partner_2.email
        # for partner in PartnerEnv.browse([application_id]).relationship_ids:
        exists = len(PartnerEnv.search([("email", "=", email_to_check)])) > 0
        return '{"exists": ' + str(exists).lower() + ',"email":"' + email_to_check + '"}'

    @http.route("/admission/checkDuplicateContact", auth="public", methods=["POST"], csrf=False)
    def check_duplicate_contact(self, **params):

        firstname_to_check = str(params['firstname']).strip();
        lastname_to_check = str(params['lastname']).strip();
        email_to_check = str(params['email']).strip();
        cellphone_to_check = str(params['cellphone']).strip();
        PartnerEnv = request.env["res.partner"].sudo();
        check_email = len(PartnerEnv.search([("email", "=ilike", email_to_check)])) > 0
        check_parent_name = len(PartnerEnv.search([("first_name", "=ilike", firstname_to_check), ("last_name", "=ilike", lastname_to_check)])) > 0
        check_cellphone = len(PartnerEnv.search([("mobile", "=", cellphone_to_check)])) > 0
        return '{"email": ' + str(check_email).lower() + ', "parent_name": ' + str(check_parent_name).lower() + ', "cellphone": ' + str(check_cellphone).lower() + '}'

    @http.route("/admission/<int:application_id>/getPhotoContact", auth="public", methods=["POST"], csrf=False)
    def getPhotoContact(self, application_id, **params):

        partner_id = params['partner_id']
        photo = request.env["adm.application"].sudo().browse([application_id]).partner_id.family_ids.member_ids.filtered(lambda partner: str(partner.id) == partner_id).image_1920

        if photo:
            return "data:image/png;base64," + str(photo)[2:-1:]
        return ""

        # return "data:image/png;base64," + str(relationship.partner_2.image_1920)[2:-1:]

    @http.route("/admission/applications/<model(adm.application):application_id>/instructions-resources", auth="public", methods=["GET"], website=True, csrf=False)
    def instructions_resources(self, application_id, **params):

        return request.render("adm.template_application_menu_instructions", self.compute_view_render_params(application_id))

    @http.route("/admission/applications/<int:application_id>/document-foreign-instructions", auth="public", methods=["GET"], website=True, csrf=False)
    def foreign_instructions_resources(self, **params):

        return request.render("adm.template_application_menu_foreign_instruc", {
            "application_id": params["application_id"],
            "application": request.env["adm.application"].browse([params["application_id"]]),
            "showPendingInformation": True if "checkData" in params else False,
            "pendingData": self.getPendingTasks(params["application_id"]),
            })

    @staticmethod
    def getPendingTasks(application_id):
        field_ids = request.env.ref("adm.model_adm_application").sudo().field_id

        # obtengo los campos el modelo admissions que sean requeridos
        FieldsEnv = request.env['ir.model.fields'].sudo()
        fields_required_ids = FieldsEnv.search([('required', '=', True)])

        keys = fields_required_ids & field_ids
        fields = [{
            "field_name": field_id.name,
            "field_descrip": field_id.field_description
            } for field_id in keys]
        result = []

        for itm in fields:
            if str(application_id[itm["field_name"]]).strip() == '':
                result.append(itm["field_descrip"])

        return result

    @http.route("/admission/applications/<model(adm.application):application_id>/info", auth="public", methods=["GET"], website=True, csrf=False)
    def info(self, application_id, **params):

        showPendingInformation = True if "checkData" in params else False
        pendingTasks = self.getPendingTasks(application_id)

        LanguageEnv = request.env["adm.language"]
        languages = LanguageEnv.browse(LanguageEnv.search([])).ids

        student_photo = "data:image/png;base64," + str(application_id.sudo().partner_id.image_1920)[2:-1:]

        # Applying semester
        field_applying_semester = request.env['adm.application']._fields['applying_semester']
        applying_semester_values = [{
            'name': name,
            'value': value
            } for value, name in field_applying_semester.selection]
        params = self.compute_view_render_params(application_id)
        params.update({
            "student": application_id.partner_id,
            "student_photo": student_photo,
            "adm_languages": languages,
            "showPendingInformation": showPendingInformation,
            "pendingData": pendingTasks,
            'applying_semester_values': applying_semester_values,
            })

        return request.render("adm.template_application_student_info", params)

    @http.route("/admission/applications/<model(adm.application):application_id>/medical-info", auth="public", methods=["GET"], website=True, csrf=False)
    def medical_info(self, application_id, **params):
        return request.render("adm.template_application_menu_medical_info", self.compute_view_render_params(application_id))

    @http.route("/admission/applications/<int:application_id>/references", auth="public", methods=["GET"], website=True, csrf=False)
    def references(self, **params):
        ApplicationEnv = request.env["adm.application"]
        application = ApplicationEnv.browse([params["application_id"]])

        return request.render("adm.template_application_menu_references", {
            "application": application,
            "application_id": params["application_id"],
            })

    @http.route("/admission/applications/<int:application_id>/document-comun", auth="public", methods=["GET"], website=True, csrf=False)
    def document_document_comun(self, **params):
        ApplicationEnv = request.env["adm.application"]
        student_application = ApplicationEnv.browse([params["application_id"]])
        AttachEnv = request.env["ir.attachment"]

        cont_comun_birth_certificate = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_birthday_certificate'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_birth_certificate = AttachEnv.sudo().browse(
                last_attach_id[0].id)  # cont_1_9_certificate_previous_school.public_url_photo = '/web/content/' + str(cont_1_9_certificate_previous_school.id) + '?download=true'

        cont_comun_member_letter = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_member_letter'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_member_letter = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_cedula_passport = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_cedula_passport'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_cedula_passport = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_healthy_certificate = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_healthy_certificate'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_healthy_certificate = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_vaccine_register = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_vaccine_register'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_vaccine_register = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_sight_certificate = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_sight_certificate'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_sight_certificate = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_oto_certificate = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_oto_certificate'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_oto_certificate = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_peace_save_certificate = 0
        last_attach_id = AttachEnv.sudo().search(
            [('name', 'like', 'comun_peace_save_certificate'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])], order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_peace_save_certificate = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_personal_reference = 0
        last_attach_id = AttachEnv.sudo().search([('name', 'like', 'comun_personal_reference'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])],
                                                 order="create_date desc", limit=1)
        if last_attach_id:
            cont_comun_personal_reference = AttachEnv.sudo().browse(last_attach_id[0].id)

        cont_comun_bank_comercial_reference = 0
        last_attach_id = AttachEnv.sudo().search(
            [('name', 'like', 'comun_bank_comercial_reference'), ('res_model', '=', 'adm.application'), ('res_id', '=', params["application_id"])], order="create_date desc",
            limit=1)
        if last_attach_id:
            cont_comun_bank_comercial_reference = AttachEnv.sudo().browse(last_attach_id[0].id)

        response_params = self.compute_view_render_params(student_application)
        response_params.update({
            "student_application": student_application,
            "cont_comun_birth_certificate": cont_comun_birth_certificate,
            "cont_comun_member_letter": cont_comun_member_letter,
            "cont_comun_cedula_passport": cont_comun_cedula_passport,
            "cont_comun_healthy_certificate": cont_comun_healthy_certificate,
            "cont_comun_vaccine_register": cont_comun_vaccine_register,
            "cont_comun_sight_certificate": cont_comun_sight_certificate,
            "cont_comun_oto_certificate": cont_comun_oto_certificate,
            "cont_comun_peace_save_certificate": cont_comun_peace_save_certificate,
            "cont_comun_personal_reference": cont_comun_personal_reference,
            "cont_comun_bank_comercial_reference": cont_comun_bank_comercial_reference,
            })
        return request.render("adm.template_application_menu_upload_file_comun", response_params)

    # definiendo la url desde donde va ser posible acceder, tipo de metodo, cors para habiltiar accesos a ip externas.
    @http.route("/admission/adm_insertId", auth="public", methods=["GET"], cors='*', csrf=False)
    # define una funcion principal
    def insertId(self, **kw):
        # return json.dumps(request.httprequest.url +' | '+ request.httprequest.base_url  +' | '+ request.httprequest.host_url)
        return json.dumps(request.httprequest.headers.environ['HTTP_ORIGIN'])
