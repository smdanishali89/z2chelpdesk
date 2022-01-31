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
	team_name_link = fields.Many2one('ecube.team', string="Team Name")
	default_team = fields.Boolean(string="Default team")
	team_name = fields.Char(string="Team Name")
	from_email_template = fields.Char(string="Email Template", compute ='_update_team_name')
	member_ids = fields.Many2many('res.users', string='Team Members' ,domain=lambda self: self._default_domain_member_ids())
	visibility_member_ids = fields.Many2many('res.users', 'helpdesk_visibility_team', string='Team Visibility', domain=lambda self: self._default_domain_member_ids(), help="Team Members to whom this team will be visible. Keep empty for everyone to see this team.")

	def _update_team_name(self):
		for record in self:
			if record.default_team == True:
				record.from_email_template = ""
			else:
				record.from_email_template = record.name






	@api.model
	def create(self, vals):
		new_record = super(team_extension, self).create(vals)
		new_record.team_name = new_record.name.lower()
		new_record.creare_ecube_team()
		return new_record

	
	def write(self, vals):
		super(team_extension, self).write(vals)
		if 'name' in vals:
			self.team_name = self.name.lower()
			self.creare_ecube_team()
		return True

	
	def creare_ecube_team(self):
		if self.team_name_link:
			self.team_name_link.name = self.name
		else:
			record = self.env['ecube.team'].create({
				'name' : self.name
				})
			self.team_name_link = record.id





class ticket_extension(models.Model):
	_inherit = ['helpdesk.ticket']



	def _default_team_id(self):
		team_id = self.env['helpdesk.team'].search([('member_ids', 'in', self.env.uid)], limit=1).id
		if not team_id:
			team_id = self.env['helpdesk.team'].search([], limit=1).id
		return team_id

	ticket_type = fields.Many2many('helpdesk.ticket.type', string="New Ticket type" , compute ='compute_ticket_type_tag')
	ticket_tag = fields.Many2many('helpdesk.tag', string="Ticket tag", compute ='compute_ticket_type_tag')
	remarks = fields.Char(string="Remarks" , track_visibility='onchange')
	reason_of_rejection = fields.Char(string="Reason" , track_visibility='onchange')
	reason_of_rejection_required = fields.Boolean(string="Reason Boll")
	remarks_required = fields.Boolean(string="Remarks Bool" )
	team_name_link = fields.Many2one('ecube.team', string="Team Name")
	team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', default=_default_team_id, index=True, track_visibility='onchange')


	def chaneg_team(self):
		if self.team_id:
			if self._uid in self.team_id.view_member_ids.ids:
				raise ValidationError('Access Denied')
		helpdesk_team = self.env['ecube.team'].sudo().search([('name','=',self.team_id.name)]).id

		return {
				'domain': [],
				'res_model': 'ecube.team.wizard',
				'type': 'ir.actions.act_window',
				'view_mode': 'form',
				'view_type': 'form',
				'context': {'default_team_users':self.domain_user_ids.ids,'default_user_id':self.user_id.id,'default_team_name_link':helpdesk_team,'default_team_name_link_invisible':helpdesk_team,'default_remarks':self.remarks},
				'target': 'new', }



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
		new_record.sudo().update_ticket_team()
		return new_record

	def write(self, vals):

		print ("write function start")
		print (vals)
		print (vals)
		print (vals)

		if 'user_id' in vals or 'team_id' in vals or 'remarks' in vals or 'remarks_required' in vals:
			pass
		else:
			if self._uid in self.team_id.view_member_ids.ids:
				raise ValidationError('Access Denied')


		# if 'user_id' in vals:
		#   if (vals['user_id']) != False:
		#       if self.team_id:
		#           if self._uid in self.team_id.view_member_ids.ids:
		#               raise ValidationError('Access Denied')
		
		# elif vals:
		#   if self.team_id:
		#       if self._uid in self.team_id.view_member_ids.ids:
		#           raise ValidationError('Access Denied')
		super(ticket_extension, self).write(vals)

		if 'stage_id' in vals and 'reason_of_rejection_required' in vals:
			if (vals['reason_of_rejection_required']) == True and not self.reason_of_rejection:
				raise ValidationError('Please add a reason for the rejection')

		if 'team_name_link' in vals:
			self.sudo().update_ticket_team()
		
		return True



class ecube_team_wizard(models.Model):
	_name = 'ecube.team.wizard'

	team_name_link_invisible = fields.Many2one('ecube.team', string="Team Name Ecube")
	team_name_link = fields.Many2one('ecube.team', string="Team Name")
	user_id = fields.Many2one('res.users', string="Assigned to")
	team_users = fields.Many2many('res.users', string="Team Users", compute ='_compute_domain_user_ids')
	remarks = fields.Char(string="Remarks" , track_visibility='onchange')
	remarks_required = fields.Boolean(string="Remarks Bool")
	


	@api.onchange('team_name_link')
	def on_chnage_of_team_remarks_required(self):
		if self.team_name_link.id == self.team_name_link_invisible.id:
			self.remarks_required = False
		else:
			self.remarks_required = True



	
	@api.depends('team_name_link')
	def _compute_domain_user_ids(self):
		for task in self:
			if task.team_name_link:
				team_id = task.env['helpdesk.team'].sudo().search([('name','=',task.team_name_link.name)])
				if team_id:
					task.team_users = team_id.visibility_member_ids.ids
					if task.user_id.id not in team_id.visibility_member_ids.ids:
						task.user_id = False

	
	def update_team(self):
		helpdesk_team = self.env['helpdesk.team'].sudo().search([('name','=',self.team_name_link.name)])
		helpdesk_ticket = self.env['helpdesk.ticket'].browse(self._context.get('active_ids'))
		helpdesk_ticket.team_id = helpdesk_team.id
		helpdesk_ticket.user_id = self.user_id.id
		helpdesk_ticket.remarks = self.remarks
		helpdesk_ticket.remarks_required = self.remarks_required

	def save_close(self):

		self.sudo().update_team()
		form_view_id = self.env.ref('helpdesk.helpdesk_team_view_kanban').id
		return {
		'type': 'ir.actions.act_window',
		'name': "New Draft Created",
		'view_type': 'kanban',
		'view_mode': 'kanban,form',
		'res_model': 'helpdesk.team',
		'views': [[form_view_id, "kanban"]],
		'view_id': form_view_id,
		'target' : 'main',
		}


class ecube_team_extension(models.Model):
	_name = 'ecube.team'

	name = fields.Char(string="Team Name")
















		