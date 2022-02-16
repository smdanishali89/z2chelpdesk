# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools.misc import get_lang

_logger = logging.getLogger(__name__)

MAPPED_RATES = {
	1: 1,
	5: 3,
	10: 5,
}

class Rating_ext(http.Controller):
	
	@http.route('/rate/<string:token>/<int:rate>', type='http', auth="public", website=True)
	def action_open_rating(self, token, rate, **kwargs):
		assert rate in (1, 3, 5), "Incorrect rating"
		rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
		if not rating:
			return request.not_found()
		if rate == 1:
			rate_names = {
				# 5: _("satisfied"),
				# 3: _("not satisfied"),
				1: _("highly dissatisfied")
			}

			rating.write({'rating': rate, 'consumed': True})
			lang = rating.partner_id.lang or get_lang(request.env).code
			
			subject = rating.resource_ref.name
			ticket_id = rating.resource_ref.id
			return request.env['ir.ui.view'].with_context(lang=lang)._render_template('help_desk_ticket.rating_external_page_submit_re_open', {
				'rating': rating, 'token': token,
				'rate_names': rate_names, 'rate': rate , 'subject': subject , 'ticket_id': ticket_id
			})
		else:
			rate_names = {
				5: _("satisfied"),
				3: _("not satisfied"),
				# 1: _("highly dissatisfied")
			}

			rating.write({'rating': rate, 'consumed': True})
			lang = rating.partner_id.lang or get_lang(request.env).code
			return request.env['ir.ui.view'].with_context(lang=lang)._render_template('rating.rating_external_page_submit', {
				'rating': rating, 'token': token,
				'rate_names': rate_names, 'rate': rate
			})
	

	@http.route(['/rate/<string:token>/submit_feedback'], type="http", auth="public", methods=['post'], website=True)
	def action_submit_rating(self, token, **kwargs):
		rate = int(kwargs.get('rate'))
		assert rate in (1, 3, 5), "Incorrect rating"
		rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
		if not rating:
			return request.not_found()
		record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
		record_sudo.rating_apply(rate, token=token, feedback=kwargs.get('feedback'))
		lang = rating.partner_id.lang or get_lang(request.env).code
		
		if rate == 1:
			stage_in_progress = request.env['helpdesk.stage'].sudo().search([('re_open_stage', '=',True)],limit=1)
			rating.resource_ref.stage_id = stage_in_progress.with_user(rating.partner_id.id).id
			# rating.resource_ref.stage_id = stage_in_progress.id
		
		return request.env['ir.ui.view'].with_context(lang=lang)._render_template('help_desk_ticket.rating_external_page_view_ext', {
			'web_base_url': request.env['ir.config_parameter'].sudo().get_param('web.base.url'),
			'rating': rating,
		})

