# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class helpdesk_mail_template_ext(models.Model):
	_inherit = ['mail.template']

	active = fields.Boolean(string="Active", default=True)




class helpdesk_mail_ext(models.Model):
	_inherit = ['mail.message']

	
	@api.model
	def create(self, vals):
		if (vals['message_type']) == "comment" and  (vals['model']) == "helpdesk.ticket":
			ticket_record = (vals['parent_id'])
			ticket_id = self.env['helpdesk.ticket'].search([('id','=',(vals['res_id']) )])
			(vals['email_from']) =  str(ticket_id.team_id.name)+' Helpdesk <helpdesk@z2climited.com>'
		
		if (vals['message_type']) == "notification" and  (vals['model']) == "helpdesk.ticket" and (vals['author_id']) == 4:
			ticket_id = self.env['helpdesk.ticket'].search([('id','=',(vals['res_id']) )])
			(vals['author_id']) =   ticket_id.partner_id.id

		new_record = super(helpdesk_mail_ext, self).create(vals)
		return new_record




class helpdesk_stage_extention(models.Model):
	_inherit = ['helpdesk.stage']

	re_open_stage = fields.Boolean(string="Re Open Stage")
	rejected_stage = fields.Boolean(string="Rejected Stage")


class team_extension(models.Model):
	_inherit = ['helpdesk.team']


	def _default_domain_member_ids(self):
		return [(1, '=', 1)]


	view_member_ids = fields.Many2many('res.users','user_member_1','user_member_1_2')
	ticket_type = fields.Many2many('helpdesk.ticket.type', string="Ticket type")
	ticket_tag = fields.Many2many('helpdesk.tag', string="Ticket tag")
	default_team = fields.Boolean(string="Default team")
	team_name = fields.Char(string="Team Name")
	member_ids = fields.Many2many('res.users', string='Team Members' ,domain=lambda self: self._default_domain_member_ids())
	visibility_member_ids = fields.Many2many('res.users', 'helpdesk_visibility_team', string='Team Visibility', domain=lambda self: self._default_domain_member_ids(), help="Team Members to whom this team will be visible. Keep empty for everyone to see this team.")



	@api.model
	def create(self, vals):
		new_record = super(team_extension, self).create(vals)
		new_record.team_name = new_record.name.lower()
		return new_record

	def write(self, vals):
		super(team_extension, self).write(vals)
		if 'name' in vals:
			self.team_name = self.name.lower()
		
		return True





class ticket_extension(models.Model):
	_inherit = ['helpdesk.ticket']

	ticket_type = fields.Many2many('helpdesk.ticket.type', string="New Ticket type" , compute ='compute_ticket_type_tag')
	ticket_tag = fields.Many2many('helpdesk.tag', string="Ticket tag", compute ='compute_ticket_type_tag')
	remarks = fields.Char(string="Remarks" , track_visibility='onchange')
	reason_of_rejection = fields.Char(string="Reason" , track_visibility='onchange')
	reason_of_rejection_required = fields.Boolean(string="Reason Boll")
	internal_description = fields.Char(string="description")
	remarks_required = fields.Boolean(string="Remarks Bool" )



	@api.onchange('team_id')
	def compute_ticket_type_tag(self):
		self.ticket_type = self.team_id.ticket_type
		self.ticket_tag = self.team_id.ticket_tag



	@api.depends('team_id')
	def _compute_domain_user_ids(self):
		for task in self:
			
			if task.team_id and task.team_id.visibility_member_ids:
				task.domain_user_ids = task.team_id.visibility_member_ids.ids
				if task.user_id.id not in task.team_id.visibility_member_ids.ids:
					task.user_id = False
			
			else:
				helpdesk_users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)]).ids
				task.domain_user_ids = [(6, 0, helpdesk_users)]
			


	@api.onchange('stage_id')
	def get_reject_reason(self):
		if self.stage_id:
			self.reason_of_rejection_required = self.stage_id.rejected_stage
			


	@api.onchange('team_id')
	def get_ticket_type(self):
		if self.ticket_type_id.id not in self.team_id.ticket_type.ids:
			self.ticket_type_id = False

		if self.team_id:
			self.remarks_required = True


	@api.onchange('team_id')
	def get_ticket_tage(self):
		tag = (self.tag_ids.ids)
		team_tag =  (self.team_id.ticket_tag.ids)
		self.tag_ids = list(set(tag).intersection(team_tag))

	
	@api.model
	def create(self, vals):
		# self.env['ir.rule'].clear_cache()
		subject = ""
		subject =  ((vals['name']).split(' ',1))[0]
		helpdesk_team = self.env['helpdesk.team'].search([('team_name','=',subject.lower())])
		if helpdesk_team:
			(vals['team_id']) = helpdesk_team.id
		else:
			default_team = self.env['helpdesk.team'].search([('default_team','=',True)], limit=1).id
			(vals['team_id']) = default_team
		
		new_record = super(ticket_extension, self).create(vals)
		new_record.compute_ticket_type_tag()
		return new_record



	def write(self, vals):
		super(ticket_extension, self).write(vals)
		if 'stage_id' in vals:
			record_id = self.env.ref('help_desk_ticket.group_helpdesk_view')
			if self.user_id.id in record_id.users.ids:
				raise ValidationError('Access Denied')

		if 'stage_id' in vals and 'reason_of_rejection_required' in vals:
			if (vals['reason_of_rejection_required']) == True and not self.reason_of_rejection:
				raise ValidationError('Please add reason of rejection')


		return True
















		