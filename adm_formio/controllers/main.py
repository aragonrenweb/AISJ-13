# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import base64
import itertools
import re
import json

from odoo import http
from odoo.http import request
from odoo.addons.adm.controllers.admission_application_controller import Admission
from odoo.exceptions import MissingError, ValidationError

_logger = logging.getLogger(__name__)

class Admission(Admission):

    @http.route("/admission/applications/message/<int:application_id>", auth="public", methods=["POST"], website=True, csrf=False)
    def send_message(self, **params):
        email = params.get("teacher_assessment_email")
        if params.get("file_upload") or not email:
            return super().send_message(**params)

        origin = params["origin"]
        application_id = int(params["application_id"])
        application = request.env["adm.application"].search([("id","=",application_id)]).sudo()
        application.teacher_assessment_email = email
        
        url_redirect = ("/admission/applications/{}/document-" + str(origin)).format(application_id)
        return request.redirect(url_redirect)