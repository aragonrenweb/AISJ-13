from ..utils import formatting

import logging
from odoo import fields, models, api, _
from odoo import api, http, models, tools, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import consteq, pycompat
from odoo.http import ALLOWED_DEBUG_MODES
_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def _get_record_and_check(self, xmlid=None, model=None, id=None, field='datas', access_token=None):
        # get object and content
        record = None
        if xmlid:
            record = self._xmlid_to_obj(self.env, xmlid)
        elif id and model in self.env:
            record = self.env[model].browse(int(id))

        # obj exists
        if not record or not record.exists() or field not in record:
            return None, 404

        allow_urls = str(self.env['ir.config_parameter'].sudo().get_param('allow_urls','')).split(',')

        if model == 'ir.attachment':
            record_sudo = record.sudo()
            if access_token and not consteq(record_sudo.access_token or '', access_token):
                return None, 403
            elif (access_token and consteq(record_sudo.access_token or '', access_token)):
                record = record_sudo
            elif record_sudo.public:
                record = record_sudo
            elif self.env.user.has_group('base.group_portal'):
                # Check the read access on the record linked to the attachment
                # eg: Allow to download an attachment on a task from /my/task/task_id
                record.check('read')
                record = record_sudo
            elif ('Origin' in http.request.httprequest.headers) and (http.request.httprequest.headers['Origin'] in allow_urls):
                record = record_sudo

            _logger.info("ORIGIN:" + str(http.request.httprequest.headers), exc_info=True)

            # con esta ruta obtenemos la ruta de origen.
        # check read access
        try:
            # We have prefetched some fields of record, among which the field
            # 'write_date' used by '__last_update' below. In order to check
            # access on record, we have to invalidate its cache first.
            record._cache.clear()
            record['__last_update']
        except AccessError:
            return None, 403

        return record, 200