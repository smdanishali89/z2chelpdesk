# -*- coding: utf-8 -*-
# from odoo import http


# class HelpDeskTicket(http.Controller):
#     @http.route('/help_desk_ticket/help_desk_ticket/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/help_desk_ticket/help_desk_ticket/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('help_desk_ticket.listing', {
#             'root': '/help_desk_ticket/help_desk_ticket',
#             'objects': http.request.env['help_desk_ticket.help_desk_ticket'].search([]),
#         })

#     @http.route('/help_desk_ticket/help_desk_ticket/objects/<model("help_desk_ticket.help_desk_ticket"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('help_desk_ticket.object', {
#             'object': obj
#         })
