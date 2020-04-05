# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import logging
from odoo import models, fields, api
from datetime import datetime, timedelta, MAXYEAR


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """ Model name: Partner
    """
    _inherit = 'res.partner'

    consultant = fields.Boolean('Consultant')


class CounselingCalendarCategory(models.Model):
    _name = 'counseling.calendar.category'
    _description = 'Counseling category'
    _order = 'name'

    name = fields.Char('Category', required=True)
    cost = fields.Float(string='Cost')
    revenue = fields.Float(string='Revenue')
    note = fields.Text(string='Note')


class CounselingCalendar(models.Model):
    _name = 'counseling.calendar'
    _description = 'Counseling calendar'
    _order = 'start_datetime'
    _inherit = ['mail.thread']

    #@api.onchange('start_datetime', 'duration')
    #def _onchange_duration(self):
    #    if self.start_datetime:
    #        self.stop = fields.Datetime.to_string(
    #            self.start_datetime + timedelta(hours=self.duration))

    name = fields.Char(
        'Meeting Subject', required=True,
        states={'closed': [('readonly', True)]})
    detail_event = fields.Text(
        string='Detail event',
        states={'closed': [('readonly', True)]},
        )
    report_event = fields.Text(
        string='Report event',
        states={'closed': [('readonly', True)]},
        )
    strategy_event = fields.Text(
        string='"Strategy event',
        states={'closed': [('readonly', True)]},
        )
    category_id = fields.Many2one(
        comodel_name='counseling.calendar.category',
        string='Category',
        required=True,
        )

    start_datetime = fields.Datetime(
        string='Start date',
        track_visibility='onchange',
        states={'closed': [('readonly', True)]},
        required=True
    )
    stop_datetime = fields.Datetime(
        string='Stop date',
    )
    duration = fields.Float(
        'Duration', states={'closed': [('readonly', True)]},
        track_visibility='onchange',
    )
    location = fields.Char(
        'Location',
        states={'closed': [('readonly', True)]},
        track_visibility='onchange',
        help='Location of Event'
    )

    # People:
    counselor_id = fields.Many2one(
        comodel_name='res.users',
        string='Counselor',
        states={'closed': [('readonly', True)]},
        track_visibility='onchange',
        required=True,
    )
    secretary_id = fields.Many2one(
        comodel_name='res.users',
        string='Secretary',
        states={'closed': [('readonly', True)]},
        help='People who take the appointment',
        default=lambda self: self._uid,
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        states={'closed': [('readonly', True)]},
        track_visibility='onchange',
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Unconfirmed'),
        ('open', 'Confirmed'),
        ('done', 'Done'),
        ('closed', 'Closed'),  # Payed
        ],
        string='Status',
        readonly=True,
        track_visibility='onchange',
        default='draft')

    cost = fields.Float(string='Cost')
    revenue = fields.Float(string='Revenue')
    # TODO Extra counselor?


'''
class CalendarEvent(models.Model):
    """ Model name: Calendar event
    """
    _inherit = 'calendar.event'

    @api.model
    def log_message(self, subject, body, message_type='notification'):
        """ Write log message
        """    
        #mail_pool = self.env['mail.thread']
        body = ("""
            <div class="o_mail_notification">
                %s
            </div>
            """) % body

        return self.sudo().message_post(
            body=body, 
            message_type=message_type, 
            subject=subject,
            )

    # Button events:
    @api.multi
    def call_skype(self):
        """ Skype call and start datatime in calendar event
        """ 
        self.log_message('Skype call', 'Inizio chiamata skype...')
        self.start_call()
        return self.patient_id.call_skype()
        
    @api.multi
    def start_call(self):
        """ Skype call and stop datatime in calendar event
        """ 
        self.log_message(
            'Chiamata telefonica', 
            'Inizio chiamata telefonica manuale')
            
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
        self.log_message(
            'Chiamata terminata', 
            'Fine chiamata telefonica o con strumenti social')

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
'''
