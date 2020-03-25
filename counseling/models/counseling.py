# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import xlsxwriter
import logging
import base64
import shutil
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    )


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """ Model name: Partner
    """
    _inherit = 'res.partner'
    
    
    consultant = fields.Boolean('Consultant')


class CalendarEvent(models.Model):
    """ Model name: Calendar event
    """
    _inherit = 'calendar.event'

    # Button events:
    @api.multi
    def call_skype(self):
        """ Skype call and start datatime in calendar event
        """ 
        self.start_call()
        return self.patient_id.call_skype()
        
    @api.multi
    def start_call(self):
        """ Skype call and stop datatime in calendar event
        """ 
        dt_now = datetime.now()
        dt_end = dt_now + timedelta(seconds=self.duration * 3600.0)
        
        return self.write({
            'start_datetime': datetime.strftime(
                dt_now, DEFAULT_SERVER_DATETIME_FORMAT),
            'stop_datetime': datetime.strftime(
                dt_end, DEFAULT_SERVER_DATETIME_FORMAT),
            'is_calling': True,
            })

    @api.multi
    def end_call(self):
        """ Skype call and stop datatime in calendar event
        """ 
        duration = datetime.now() - datetime.strptime(
            self.start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
            
        return self.write({
            'duration': duration.total_seconds() / 3600.0,
            'is_calling': False,
            })
        
    # -------------------------------------------------------------------------
    #                                   COLUMNS:
    # -------------------------------------------------------------------------
    is_calling = fields.Boolean('Is calling')

    patient_id = fields.Many2one('medical.patient', 'Paziente', required=True)
    skype_name = fields.Char(
        'Skype name', size=64, related='patient_id.skype_name')
    telegram_name = fields.Char(
        'Telegram name', size=64, related='patient_id.telegram_name')
    hangout_name = fields.Char(
        'Hangout name', size=64, related='patient_id.hangout_name')


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
    def social_url(self, social='skype', mode='call'):
        """ Call skype URL
            skype:username?<mode>
        """
        name = 'Social media: %s mode: %s' % (social, mode)
        
        if social == 'skype':
            url = 'skype:%s?%s' % (self.skype_name, mode)

        elif social == 'telegram':
            if mode == 'call':
                return False
            url = 'https://t.me/%s' % self.telegram_name

        _logger.info('Calling: %s' % url)
        return {
            'name': name,
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
            }
            
    # -------------------------------------------------------------------------
    # SKYPE:
    # -------------------------------------------------------------------------
    @api.multi
    def call_skype(self):
        """ Call skype call link
        """
        return self.social_url('skype', 'call')
        
    @api.multi
    def chat_skype(self):
        """ Call skype chat link
        """
        return self.social_url('skype', 'chat')

    # -------------------------------------------------------------------------
    # TELEGRAM:
    # -------------------------------------------------------------------------
    @api.multi
    def call_telegram(self):
        """ Call Telegram call link
        """
        return self.social_url('telegram', 'call')
        
    @api.multi
    def chat_telegram(self):
        """ Call Telegram chat link
        """
        return self.social_url('telegram', 'chat')

    # Columns:
    skype_name = fields.Char('Skype name', size=64)
    telegram_name = fields.Char('Telegram name', size=64)
    hangout_name = fields.Char('Hangout name', size=64)

