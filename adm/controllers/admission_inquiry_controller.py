# -*- coding: utf-8 -*-
from odoo import http
from ..utils import formatting
import base64


def get_parameters():
    return http.request.httprequest.args


def post_parameters():
    return http.request.httprequest.form


class Admission(http.Controller):

    #===================================================================================================================
    # @http.route("/")
    # def
    #===================================================================================================================

    @http.route("/admission/inquiry", auth="public", methods=["GET"], website=True)
    def admission_web(self, **params):
        countries = http.request.env['res.country'].sudo()
        states = http.request.env['res.country.state'].sudo()
        contact_times = http.request.env['adm.contact_time']
        degree_programs = http.request.env['adm.degree_program']

        grade_level = http.request.env['school_base.grade_level']
        school_year = http.request.env['school_base.school_year']

        family_id = -1

        if 'family_id' in params:
            family_id = params['family_id']

        response = http.request.render('adm.template_admission_inquiry', {
            'grade_levels': grade_level.search([('active_admissions', '=', True)]),
            'school_years': school_year.search([]),
            'countries': countries.search([]),
            'states': states.search([]),
            'contact_times': contact_times.search([]),
            'degree_programs': degree_programs.search([]),
            'check_family_id': True,
            'family_name': '',
            'family_id': family_id,
        })
        return response

    def all_exist(avalue, bvalue):
        return all(any(x in y for y in bvalue) for x in avalue)

    @http.route("/admission/inquiry", auth="public", methods=["POST"], website=True, csrf=False)
    def add_inquiry(self, **params):

        PartnerEnv = http.request.env['res.partner']

        if "txtMiddleName_1" not in params:
            params["txtMiddleName_1"] = ""

        if "txtResidePanama_1" not in params:
            params["txtResidePanama_1"] = False
        else:
            params["txtResidePanama_1"] = True

        community_street_address = ''

        if 'checkbox_family_id' in params and params["checkbox_family_id"] == 'on':
            family_id_fact = params["input_family_id"]
            #'mobile': mobile_1,
            #'phone': phone_1,
            #'email': email_1,
            #'responsible_id': [(6, 0, parents_ids_created)],

            # PARA TOMAR POR FACTS ID
            # if len(PartnerEnv.sudo().search([('facts_id','=',family_id_fact),('is_family', '=', True)])) == 0:
            # CASO DE TOMAR POR EL FACTS UD ID
            if len(PartnerEnv.sudo().search([('facts_id', '=', family_id_fact), ('is_family', '=', True)])) == 0:
                countries = http.request.env['res.country']
                states = http.request.env['res.country.state']
                contact_times = http.request.env['adm.contact_time']
                degree_programs = http.request.env['adm.degree_program']
                grade_level = http.request.env['school_base.grade_level']
                school_year = http.request.env['school_base.school_year']

                response = http.request.render('adm.template_admission_inquiry', {
                    'grade_levels': grade_level.search([('active_admissions', '=', True)]),
                    'school_years': school_year.search([]),
                    'countries': countries.search([]),
                    'states': states.search([]),
                    'contact_times': contact_times.search([]),
                    'degree_programs': degree_programs.search([]),
                    #'': PartnerEnv.sudo().search([('email', '=', email_1),('is_family', '=', True)]),
                    'check_family_id': False,
                    'family_name': '',
                    'parent': False,
                })
                return response
            else:
                # PARA TOMAR POR FACTS ID
                #   family_data = PartnerEnv.sudo().search([('facts_id','=',family_id_fact),('is_family', '=', True)])[0]
                # CASO DE TOMAR POR EL FACTS UD ID
                family_data = PartnerEnv.sudo().search([('facts_id','=',family_id_fact),('is_family', '=', True)])[0]
                family_id = family_data
                mobile_1 = family_data.mobile
                phone_1 = family_data.phone
                email_1 = family_data.email
                country_id = family_data.country_id.id
                parents_ids_created = (family_data.member_ids.filtered(lambda item: item.function == 'parent')).ids

        else:
            # Create a new family
            full_name = "{}, {}{}".format(params["txtLastName_1"],
                                           params["txtFirstName_1"],
                                           "" if not params["txtMiddleName_1"] else " {}".format(params["txtMiddleName_1"]))

            first_name = params["txtFirstName_1"]
            middle_name = params["txtMiddleName_1"]
            last_name = params["txtLastName_1"]
            country_id = int(params["selCountry_1"])
            resident_panama = bool(params["txtResidePanama_1"])
            # state = int(params["selState"]) if params["selState"] else False
            # zip = params["txtZip"]

            mobile_1 = params["txtCellPhone_1"]
            phone_1 = params["txtHomePhone_1"]
            email_1 = params["txtEmail_1"]

            family_1 = ''
            if 'selFamily_1' in params:
                family_1 = params["selFamily_1"]
            # city = params["txtCity"]

            # FAMILY DATA/admission/inquiry

            if "txtStreetAddress" in params:
                community_street_address = params["txtStreetAddress"]


            # FAMILY DATA/admission/inquiry
            inquiry_street_address = ''
            if "inquiry_street_address" in params:
                inquiry_street_address = params["inquiry_street_address"]

            inquiry_zip = ''
            if "inquiry_zip" in params:
                inquiry_zip = params["inquiry_zip"]

            inquiry_city = ''
            if "inquiry_city" in params:
                inquiry_city = params["inquiry_city"]

            inquiry_state_id = ''
            if "inquiry_state_id" in params:
                inquiry_state_id = int(params["inquiry_state_id"])

            inquiry_country_id = ''
            if "inquiry_country_id" in params:
                inquiry_country_id = int(params["inquiry_country_id"])


            # context = "{'member_id': active_id, 'default_street': street,
            # 'default_is_company': True, 'default_is_family': True,
            # 'default_street2': street2, 'default_city': city,
            # 'default_state_id': state_id, 'default_zip': zip,
            # 'default_country_id': country_id, 'default_lang': lang,
            # 'default_user_id': user_id}

            # PartnerEnv.search([('email','=',email_1)])
    # PartnerEnv.browse(PartnerEnv.sudo().search([('email','=','dconde@eduwebgroup.com')]).family_ids)[2].id.name

            partner_body = {
                    "name": "{} family".format(last_name),
                    "company_type": "company",
                    "is_family": True,
                    # "street": inquiry_street_address,
                    # "zip": inquiry_zip,
                    # "city":inquiry_city,
                    # "country_id":inquiry_country_id,
                    'mobile': mobile_1,
                    'phone': phone_1,
                    'email': email_1,
                }

            if inquiry_state_id != '':
                partner_body["state_id"] = inquiry_state_id

            if family_1 is '':
                family_id = PartnerEnv.sudo().create(partner_body)
                parent_id_1 = PartnerEnv.sudo().create({
                    "name": full_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "parent_id": family_id.id,
                    "function": "parent",
                    "family_ids": [(6,0,[family_id.id])],
                    # "street": inquiry_street_address,
                    # "zip": inquiry_zip,
                    # "city":inquiry_city,
                    # "state_id":inquiry_state_id,
                    "country_id":country_id,
                    "is_resident_panama": resident_panama,
                    'mobile': mobile_1,
                    'phone': phone_1,
                    'email': email_1,
                })
            else:
                family_id = PartnerEnv.sudo().search([('id', '=', family_1)])
                parent_id_1 = PartnerEnv.sudo().search([('email','=',email_1),('function', '=', 'parent')])[0]

            parents_ids_created = []
            family_id.write({'member_ids': [(4,parent_id_1.id)]})
            parents_ids_created.append(parent_id_1.id)

            if "txtMiddleName_2" not in params:
                params["txtMiddleName_2"] = ""
            if "txtResidePanama_2" not in params:
                params["txtResidePanama_2"] = False

            # Create a new family full_name = "{}, {}{}".format(params["txtLastName_1"], params["txtFirstName_1"],
            # "" if not params["txtMiddleName_1"] else " {}".format(params["txtMiddleName_1"]))
            #arrayData = ["txtFirstName_2", "txtLastName_2", "selCountry_2", "txtCellPhone_2", "txtHomePhone_2","txtEmail_2"]
            #if self.all_exist(arrayData, params):

            if all (k in params for k in ("txtFirstName_2", "txtLastName_2", "selCountry_2", "txtCellPhone_2", "txtHomePhone_2","txtEmail_2")):
                first_name = params["txtFirstName_2"]
                middle_name = params["txtMiddleName_2"]
                last_name = params["txtLastName_2"]
                country_id = int(params["selCountry_2"])
                resident_panama = bool(params["txtResidePanama_2"])
                full_name = "{}, {}{}".format(params["txtLastName_2"], params["txtFirstName_2"],
                                              "" if not params["txtMiddleName_2"] else " {}".format(
                                                  params["txtMiddleName_2"]))
                mobile_2 = params["txtCellPhone_2"]
                phone_2 = params["txtHomePhone_2"]
                email_2 = params["txtEmail_2"]

                if len(PartnerEnv.sudo().search([('email', '=', email_2), ('function', '=', 'parent')])) > 0:
                    parent_id_2 = PartnerEnv.sudo().search([('email', '=', email_2), ('function', '=', 'parent')])[0]
                    parent_id_2.write({'family_ids': [(4,family_id.id)]})
                else:
                    parent_id_2 = PartnerEnv.sudo().create({
                        "name": full_name,
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "parent_id": family_id.id,
                        "function": "parent",
                        "family_ids": [(6, 0, [family_id.id])],
                        "is_resident_panama": resident_panama,
                        "country_id": country_id,
                        'mobile': mobile_2,
                        'phone': phone_2,
                        'email': email_2,
                    })

                parents_ids_created.append(parent_id_2.id)
                family_id.write({'member_ids': [(4, parent_id_2.id)]})
        # Create students
        id_students = list()
        students_total = int(params["studentsCount"])

        first_name_list = post_parameters().getlist("txtStudentFirstName")
        last_name_list = post_parameters().getlist("txtStudentLastName")
        middle_name_list = post_parameters().getlist("txtStudentMiddleName")
        birthday_list = post_parameters().getlist("txtStudentBirthday")
        grade_level_list = list(map(int, post_parameters().getlist("selStudentGradeLevel")))
        school_year_list = list(map(int, post_parameters().getlist("selStudentSchoolYear")))
        current_school_list = post_parameters().getlist("txtStudentCurrentSchool")
        gender_list = post_parameters().getlist("selStudentGender")
 
        InquiryEnv = http.request.env["adm.inquiry"]

        text_reference_a = ''
        if "txtReferenceFamily_1_a" in params:
            text_reference_a = params["txtReferenceFamily_1_a"]

        text_reference_b = ''
        if "txtReferenceFamily_1_b" in params:
            text_reference_b = params["txtReferenceFamily_1_b"]

        if "title_1" not in params:
            params["title_1"] = ''

        congre_member = params["title_1"]

        if congre_member is 'other':
            congre_member = params["other_reason_1"]

        #member_ids_created = parents_ids_created

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
            full_name_student = "{}, {}{}".format(last_name, first_name, "" if not middle_name else " {}".format(middle_name))
 
            id_student = PartnerEnv.sudo().create({
                "name": full_name_student,
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "parent_id": family_id.id,
                "function": "student",
                "person_type": "student",
                "family_ids": [(6, 0, [family_id.id])],
                #"street": street,
                # "country_id": country_id,
                'date_of_birth': birthday,
                'mobile': mobile_1,
                'phone': phone_1,
                'email': email_1,
            })
            #member_ids_created.append(id_student.id)
            family_id.write({'member_ids': [(4, id_student.id)]})

            # Create an inquiry for each new student
            new_inquiry = InquiryEnv.sudo().create({
                "partner_id": id_student.id,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'gender': http.request.env.ref('adm.{}'.format(gender)).id,
                'community_street_address': community_street_address,
                'reference_family_1': text_reference_a,
                'reference_family_2': text_reference_b,
                'congregation_member': congre_member,
                'school_year_id': school_year,
                'grade_level_id': grade_level,
                'current_school': current_school,
#                'current_school_address': current_school_address,
                'responsible_id': [(6,0,parents_ids_created)],
                # 'responsible_id': parent_id.id


            })
            
            id_student.inquiry_id = new_inquiry.id
            id_students.append(id_student)

        # family_created = PartnerEnv.browse(family_id[0].id)
        #
        # family_created.sudo().write({
        #     'member_ids': [(6,0,member_ids_created)],
        # })

        response = http.request.render('adm.template_inquiry_sent')
        return response

