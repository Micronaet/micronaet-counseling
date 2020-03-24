# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import xlsxwriter
import logging
import base64
import shutil
from odoo import models, fields, api

_logger = logging.getLogger(__name__)



class CalendarEvent(models.Model):
    """ Model name: Calendar event
    """
    _inherit = 'calendar.event'

    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    patient_id = fields.Many2one('medical.patient', 'Paziente', required=True)


class MedicalPatient(models.Model):
    """ Model name: Calendar event
    """
    
    _inherit = 'medical.patient'
    
    # Button events:
    # TODO 
    # Add: skype:username?add
    # View profile: skype:username?userinfo
    # Leave a voicemail: skype:username?voicemail
    # Send file: skype:username?sendfile
    
    @api.model
    def skype_url(self, mode='call'):
        """ Call skype URL
            skype:username?<mode>
        """
        return {
            'name': 'Skype mode: %s' % mode
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': 'skype:%s?%s' % (self.skype_name, mode),
            }

    @api.multi
    def call_skype(self):
        """ Call skype call link
        """
        return self.skype_url('call')
        
    @api.multi
    def chat_skype(self):
        """ Call skype chat link
        """
        return self.skype_url('chat')

    # Columns:
    skype_name = fields.Char('Skype name', size=64)
    telegram_name = fields.Char('Telegram name', size=64)
    hangout_name = fields.Char('Hangout name', size=64)

