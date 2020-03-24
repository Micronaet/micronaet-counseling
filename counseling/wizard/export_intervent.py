#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<https://micronaet.com>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import logging
import odoo
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

class CalendarEventExcelReportWizard(models.TransientModel):
    """ Model name: CalendarEventExcelReportWizard
    """
    _name = 'calendar.event.excel.report.wizard'
    _description = 'Extract event wizard'
    
    # -------------------------------------------------------------------------
    #                            COLUMNS:
    # -------------------------------------------------------------------------    
    doctor_id = fields.Many2one('res.users', 'Doctor')
    patient_id = fields.Many2one('medical.patient', 'Patient')
    
    from_date = fields.Date('From date >=', required=True)
    to_date = fields.Date('To date <', required=True)
    privacy = fields.Boolean(
        'Privacy', help='Hide patient data and intervent', default=True)
    
    # -------------------------------------------------------------------------    

    @api.model
    def format_hour(self, float_time):
        """ Float time converter
        """
        if abs(float_time) < 0.000001:
            return '0:00'
        
        hour = int(float_time)
        minute = int((float_time - hour) * 60.0)
        return '%s:%02d' % (hour, minute)
        
    @api.multi
    def extract_event_report(self):
        ''' Extract Excel report
        '''        
        move_pool = self.env['calendar.event']
        excel_pool = self.env['excel.report']
        
        # Wizard parameters:
        from_date = self.from_date
        to_date = self.to_date
        doctor = self.doctor_id
        patient = self.patient_id
        privacy = self.privacy
        
        domain = [
            # Header
            ('start_datetime', '>=', '%s 00:00:00' % from_date),
            ('start_datetime', '<', '%s 00:00:00' % to_date),
            ]

        #if doctor:
        #    domain.append(
        #        ('partner_ids.id', '=', doctor.id),
        #        )

        if patient:
            domain.append(
                ('patient_id', '=', patient.id),
                )
                
        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Excel file configuration: # TODO
        header = ('Data', 'Alle', 'Durata', 'Dottore', 'Paziente')
        column_width = (18, 18, 7, 25, 25)

        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------        
        ws_name = 'Dettaglio'
        excel_pool.create_worksheet(ws_name, format_code='DEFAULT')        
        excel_pool.column_width(ws_name, column_width)

        row = 0
        excel_pool.write_xls_line(ws_name, row, [
            u'Interventi con filtro: [Consulente %s], [Paziente %s], Periodo [%s, %s]' % (
                (doctor.partner_id.name if doctor else 'Tutti'),
                (patient.name if patient else 'Tutti'),
                from_date,
                to_date,
                )
            ], style_code='title')
            
        row += 2
        excel_pool.write_xls_line(ws_name, row, header, 
            style_code='header')
        for move in sorted(move_pool.search(domain), 
                key=lambda x: x.start_datetime):
            row += 1
            partner = move.partner_ids[0]
            if doctor.partner_id.id != partner.id:
                continue
            if privacy:
                patient_name = move.patient_id.name
            else:
                patient_name = move.patient_id.patient_id.name
                
            excel_pool.write_xls_line(ws_name, row, [
                move.start_datetime,
                move.stop_datetime,
                (self.format_hour(move.duration), 'number'),
                partner.name,
                patient_name,
                ], style_code='text')
                    

        return excel_pool.return_attachment('report_interventi')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
