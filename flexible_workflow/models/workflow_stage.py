# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class WorkflowStage(models.Model):
    _name = "workflow.stage"
    _description = "Workflow Stage"

    name = fields.Char(string="Name",
        required=True)
    sequence = fields.Integer(string="Sequence")
    workflow_id = fields.Many2one(string="Workflow",
        comodel_name="workflow.workflow",
        required=True,
        ondelete="cascade")
    group_ids = fields.Many2many(string="Groups",
        comodel_name="res.groups")
    user_ids = fields.Many2many(string="Users",
        comodel_name="res.users")
    attribute_ids = fields.One2many(string="Attributes",
        comodel_name="workflow.attribute",
        inverse_name="stage_id")