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

import logging
from odoo import api, fields, models, tools, exceptions, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class CalendarEventExcelReportWizard(models.TransientModel):
    """ Model name: CalendarEventExcelReportWizard
    """
    _name = 'calendar.event.excel.report.wizard'
    _description = 'Extract event wizard'

    # -------------------------------------------------------------------------
    #                            COLUMNS:
    # -------------------------------------------------------------------------
    counselor_id = fields.Many2one('res.users', 'Counselor')
    patient_id = fields.Many2one('res.partner', 'Patient')
    category_id = fields.Many2one('counseling.calendar.category', 'Category')

    from_date = fields.Date('From date >=')  # required=True)
    to_date = fields.Date('To date <')  # required=True)
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
        """ Extract Excel report
        """
        attendance_pool = self.env['counseling.calendar']
        excel_pool = self.env['excel.report']

        # Wizard parameters:
        from_date = self.from_date
        to_date = self.to_date

        counselor = self.counselor_id
        patient = self.patient_id

        category = self.category_id
        privacy = self.privacy

        domain = []
        if from_date:
            domain.append(
                ('start_datetime', '>=', '%s 00:00:00' % from_date),
            )
        if to_date:
            domain.append(
                ('start_datetime', '<', '%s 23:59:59' % to_date),
            )

        if counselor:
            domain.append(
                ('counselor_id', '=', counselor.id),
                )
        if patient:
            domain.append(
                ('partner_id', '=', patient.id),
                )
        if category:
            domain.append(
                ('category_id', '=', category.id),
                )

        # ---------------------------------------------------------------------
        #                          EXTRACT EXCEL:
        # ---------------------------------------------------------------------
        # Excel file configuration: # TODO
        header = (
            'Data', 'Alle', 'Durata', 'Paziente', 'Consulente', 'Categoria')
        column_width = (18, 18, 7, 25, 30, 25)

        # ---------------------------------------------------------------------
        # Write detail:
        # ---------------------------------------------------------------------
        ws_name = 'Dettaglio'
        excel_pool.create_worksheet(ws_name, format_code='DEFAULT')
        excel_pool.column_width(ws_name, column_width)

        row = 0
        excel_pool.write_xls_line(ws_name, row, [
            u'Interventi con filtro: [Consulente %s], [Paziente %s], '
            'Periodo [%s, %s], [Categoria %s]' % (
                counselor.partner_id.name if counselor else 'Tutti',
                patient.name if patient else 'Tutti',
                from_date or '/',
                to_date or '/',
                category.name if category else 'Tutte',
                )
            ], style_code='title')

        row += 2
        excel_pool.write_xls_line(ws_name, row, header,
                                  style_code='header')
        total = 0.0
        for attendance in sorted(attendance_pool.search(domain),
                                 key=lambda x: x.start_datetime):
            if privacy:
                patient_name = 'ID %s' % attendance.partner_id.id
            else:
                patient_name = attendance.partner_id.name

            total += attendance.duration
            row += 1
            excel_pool.write_xls_line(ws_name, row, [
                #attendance_pool.date_to_datetime(attendance.start_datetime),
                attendance.start_datetime,
                attendance.stop_datetime,
                (self.format_hour(attendance.duration), 'number'),
                patient_name,
                attendance.counselor_id.name,
                attendance.category_id.name or '/',
                ], style_code='text')

        row += 1
        excel_pool.write_xls_line(ws_name, row, [
            'Totale',
            (self.format_hour(total), 'number'),
            ], style_code='text', col=1)

        return excel_pool.return_attachment('report_interventi')
