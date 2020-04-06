# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """ Model name: Partner
    """
    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    # Button events:
    # -------------------------------------------------------------------------
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

    consultant = fields.Boolean('Consultant')
    patient = fields.Boolean('Patient')


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

    # -------------------------------------------------------------------------
    # Button events:
    # -------------------------------------------------------------------------
    @api.multi
    def call_skype(self):
        """ Skype call and start datetime in calendar event
        """
        self.start_call('skype')
        return self.partner_id.call_skype()

    @api.multi
    def start_call_manual(self):
        self.start_call('manuale')

    @api.multi
    def end_call_manual(self):
        """ Skype call and stop datetime in calendar event
        """
        self.log_message(
            'Chiamata terminata',
            'Fine chiamata telefonica o con strumenti social')

        duration = datetime.now() - datetime.strptime(
            self.start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)

        return self.write({
            'duration': duration.total_seconds() / 3600.0,
            'state': 'done',
        })

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    @api.model
    def start_call(self, mode):
        """ Skype call and stop datatime in calendar event
        """
        self.log_message(
            'Chiamata telefonica',
            'Inizio chiamata telefonica %s' % mode)

        dt_now = datetime.now()
        #dt_end = dt_now + timedelta(seconds=self.duration * 3600.0)

        return self.write({
            'start_datetime': datetime.strftime(
                dt_now, DEFAULT_SERVER_DATETIME_FORMAT),
            # 'stop_datetime': datetime.strftime(
            #    dt_end, DEFAULT_SERVER_DATETIME_FORMAT),
            # 'is_calling': True,
        })

    # -------------------------------------------------------------------------
    # workflow button
    # -------------------------------------------------------------------------
    @api.multi
    def wkf_go_draft(self):
        """ Go in draft mode
        """
        return self.write({'state': 'draft'})

    @api.multi
    def wkf_go_open(self):
        """ Go in open mode
        """
        return self.write({'state': 'open'})

    @api.multi
    def wkf_go_done(self):
        """ Go in done mode
        """
        return self.write({'state': 'done'})

    @api.multi
    def wkf_go_closed(self):
        """ Go in closed mode
        """
        return self.write({'state': 'closed'})

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------
    @api.model
    def log_message(self, subject, body, message_type='notification'):
        """ Write log message
        """
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

    @api.model
    def date_to_datetime(self, userdate):
        """ Convert date values expressed in user's timezone to
        server-side UTC timestamp, assuming a default arbitrary
        time of 12:00 AM - because a time is needed.

        :param str userdate: date string in in user time zone
        :return: UTC datetime string for server-side use
        """
        import pdb; pdb.set_trace()
        context = self.env.context
        user_date = datetime.strptime(
            userdate[:10],
            DEFAULT_SERVER_DATE_FORMAT)
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.env['res.users'].browse(self.uid).tz
        if tz_name:

            import pytz
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date + relativedelta(hours=12.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            '''
            import pytz
            utc = pytz.timezone('UTC')
            user_datetime = datetime.strptime(
                userdate,
                DEFAULT_SERVER_DATETIME_FORMAT)


            context_tz = pytz.timezone(tz_name)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            '''
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.depends('start_datetime', 'duration')
    def _get_stop_datetime(self):
        """ Calc end datetime
        """
        for attend in self:
            if attend.start_datetime and attend.duration:
                start_dt = datetime.strptime(
                    attend.start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                attend.stop_datetime = fields.Datetime.to_string(
                    start_dt + timedelta(hours=attend.duration))
            else:
                attend.stop_datetime = False

    # @api.onchange('start_datetime', 'duration')
    # def _onchange_duration(self):
    #     if self.start_datetime:
    #         self.stop = fields.Datetime.to_string(
    #             self.start_datetime + timedelta(hours=self.duration))

    name = fields.Char(
        'Meeting Subject', required=True,
        states={'closed': [('readonly', True)]})
    detail_event = fields.Text(
        string='Argument appointment',
        states={'closed': [('readonly', True)]},
        )
    report_event = fields.Text(
        string='Result appointment',
        states={'closed': [('readonly', True)]},
        )
    strategy_event = fields.Text(
        string='Strategy appointment',
        states={'closed': [('readonly', True)]},
        )
    category_id = fields.Many2one(
        comodel_name='counseling.calendar.category',
        string='Category',
        required=True,
        states={'closed': [('readonly', True)]},
        )

    start_datetime = fields.Datetime(
        string='Start date',
        track_visibility='onchange',
        states={'closed': [('readonly', True)]},
        required=True,
    )
    stop_datetime = fields.Datetime(
        string='Stop date',
        compute='_get_stop_datetime',
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
        # track_visibility='onchange',
        required=True,
    )
    secretary_id = fields.Many2one(
        comodel_name='res.users',
        string='Taken by',
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

    skype_name = fields.Char(
        'Skype name', size=64, related='partner_id.skype_name')
    telegram_name = fields.Char(
        'Telegram name', size=64, related='partner_id.telegram_name')
    hangout_name = fields.Char(
        'Hangout name', size=64, related='partner_id.hangout_name')

    cost = fields.Float(
        string='Cost',
        states={'closed': [('readonly', True)]},
    )
    revenue = fields.Float(
        string='Revenue',
        states={'closed': [('readonly', True)]},
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

    # TODO Extra counselor?
