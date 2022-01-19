# -*- coding: utf-8 -*-

from odoo import models, fields, api


class helpdesk_stage_extention(models.Model):
	_inherit = ['helpdesk.stage']

	in_progress_stage = fields.Boolean(string="In Progress")


class team_extension(models.Model):
	_inherit = ['helpdesk.team']

	ticket_type = fields.Many2many('helpdesk.ticket.type', string="Ticket type")
	ticket_tag = fields.Many2many('helpdesk.tag', string="Ticket tag")
	default_team = fields.Boolean(string="Default team")





class ticket_extension(models.Model):
	_inherit = ['helpdesk.ticket']

	ticket_type = fields.Many2many('helpdesk.ticket.type', string="New Ticket type" , compute ='compute_ticket_type')
	ticket_tag = fields.Many2many('helpdesk.tag', string="Ticket tag", compute ='compute_ticket_tag')



	@api.onchange('team_id')
	def compute_ticket_type(self):
		self.ticket_type = self.team_id.ticket_type



	def compute_ticket_tag(self):
		self.ticket_tag = self.team_id.ticket_tag


	@api.model
	def create(self, vals):
		subject = ""
		subject =  ((vals['name']).split(' ',1))[0]
		default_team = self.env['helpdesk.team'].search([('default_team','=',True)], limit=1).id
		if subject:
			helpdesk_team = self.env['helpdesk.team'].search([('name','=',subject)])
			if helpdesk_team:
				(vals['team_id']) = helpdesk_team.id
			else:
				(vals['team_id']) = default_team
		else:
			(vals['team_id']) = default_team
		
		new_record = super(ticket_extension, self).create(vals)

		return new_record
















        