# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import UserError, AccessError

class WorkflowMixin(models.AbstractModel):
    _name = "workflow.mixin"
    _description = "Workflow Mixin"

    workflow_stage_id = fields.Many2one(string="Workflow Stage",
        comodel_name="workflow.stage",
        tracking=True)
    prev_workflow_stage_id = fields.Many2one(string="Previous Workflow Stage",
        comodel_name="workflow.stage",
        compute="_compute_prev_workflow_stage_id")
    next_workflow_stage_id = fields.Many2one(string="Next Workflow Stage",
        comodel_name="workflow.stage",
        compute="_compute_next_workflow_stage_id")

    def _compute_prev_workflow_stage_id(self):
        for rec in self:
            result = False
            if rec.workflow_stage_id:
                stage_ids = rec.workflow_stage_id.workflow_id.stage_ids.ids
                current_stage_index = stage_ids.index(rec.workflow_stage_id.id)
                if current_stage_index > 0:
                    result = stage_ids[current_stage_index - 1]
            rec.prev_workflow_stage_id = result

    def _compute_next_workflow_stage_id(self):
        for rec in self:
            result = False
            if rec.workflow_stage_id:
                stage_ids = rec.workflow_stage_id.workflow_id.stage_ids.ids
                current_stage_index = stage_ids.index(rec.workflow_stage_id.id)
                if current_stage_index < (len(stage_ids) - 1):
                    result = stage_ids[current_stage_index + 1]
            rec.next_workflow_stage_id = result

    def action_next_workflow_stage(self):
        self.ensure_one()
        if not self.workflow_stage_id:
            raise UserError("Record is currently not in any stage")
        if not self.next_workflow_stage_id:
            raise UserError("This is already in the last stage of the workflow")
        self._check_access()
        self.workflow_stage_id = self.next_workflow_stage_id.id

    def action_prev_workflow_stage(self):
        self.ensure_one()
        if not self.workflow_stage_id:
            raise UserError("Record is currently not in any stage")
        if not self.prev_workflow_stage_id:
            raise UserError("This is already in the first stage of the workflow")
        self._check_access()
        self.workflow_stage_id = self.prev_workflow_stage_id.id
    
    def _check_access(self):
        self.ensure_one()
        group_allow = False
        user_allow = False
        message = ""
        if self.workflow_stage_id.group_ids:
            group_allow = bool(self.workflow_stage_id.group_ids & self.env.user.groups_id)
            message += "\nGroups: " + ", ".join(self.workflow_stage_id.group_ids.mapped("full_name"))
        if self.workflow_stage_id.user_ids:
            user_allow = bool(self.workflow_stage_id.user_ids & self.env.user)
            message += "\nUsers: " + ", ".join(self.workflow_stage_id.user_ids.mapped("name"))
        if not ((not self.workflow_stage_id.group_ids and not self.workflow_stage_id.user_ids) or group_allow or user_allow):
            raise AccessError("Only the following can change stage from the current stage:" + message)

    @api.model
    def default_get(self, fields):
        res = super(WorkflowMixin, self).default_get(fields)
        workflow = self.env["workflow.workflow"].search([("model_id","=",self.env["ir.model"]._get(self._name).id)])
        if workflow:
            res["workflow_stage_id"] = workflow.stage_ids and workflow.stage_ids[0].id or False
        return res