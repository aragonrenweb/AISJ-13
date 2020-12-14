# -*- coding: utf-8 -*-
import logging
from odoo import http
from datetime import datetime
import base64
import itertools
import re
import json
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response

_logger = logging.getLogger(__name__)


class ExternalLogin(http.Controller):
    @http.route("/admission/logging_from_facts", auth="public",
                methods=["GET"],
                website=True)
    def logging_from_facts(self, **params):
        # allow_urls = (request.env['ir.config_parameter'].sudo()
        #               .get_param('allow_urls', ''))
        # admin_pass = (request.env['ir.config_parameter'].sudo()
        #               .get_param('admin_pass', ''))
        if 'parent_email' in params and params['parent_email']:
            parent_email = params['parent_email']
            user_id = (request.env["res.users"].sudo()
                    .search([('email', '=ilike', parent_email)]))
            if user_id:
                # uid = request.session.authenticate(
                #     request.session.db,
                #     'admin',
                #     admin_pass)

                request.session.uid = user_id.id
                request.session.login = parent_email
                request.params['login_success'] = True

        page = params.get('page', '')
        family_id = params.get('family_id', '')
        route = '/admission/%s?family_id=%s' % (page, family_id)

        return request.redirect(route)
        # if ('HTTP_ORIGIN' in request.httprequest.headers.environ):
        #     origen_url = request.httprequest.headers.environ['HTTP_ORIGIN']
        #
        # ApplicationEnv = request.env["adm.application"]
        #
        # application_ids = ApplicationEnv.sudo().search([("family_id", "=", 481)])
        #
        # response = request.render('adm.template_admission_application_list', {
        #     "application_ids": application_ids,
        # })
        # return response
