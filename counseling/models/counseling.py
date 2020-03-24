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
    
    skype_name = fields.Char('Skype name', size=64)
    telegram_name = fields.Char('Telegram name', size=64)
    hangout_name = fields.Char('Hangout name', size=64)

