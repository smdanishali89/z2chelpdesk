# -*- coding: utf-8 -*-

from odoo import models, fields, api


class team_extension(models.Model):
	_inherit = ['helpdesk.team']

	ticket_type = fields.Many2many('helpdesk.ticket.type', string="Ticket type")
	ticket_tag = fields.Many2many('helpdesk.tag', string="Ticket tag")





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


		helpdesk_team = self.env['helpdesk.team'].search([])
		if helpdesk_team:
			for team in helpdesk_team:
				ticket_name = ""
				ticket_name = ""
				
				ticket_name = (vals['name'])
				team_name = team.name
				if team_name.lower() in ticket_name.lower():

					(vals['team_id']) = team.id
				else:
				    print("Not found!")

		new_record = super(ticket_extension, self).create(vals)

		return new_record















        