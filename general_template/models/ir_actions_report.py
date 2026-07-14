# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

import io
import os
import base64
import tempfile
import logging
from contextlib import closing
from odoo.exceptions import UserError
from PyPDF2 import PdfFileWriter, PdfFileReader
from odoo.tools.misc import find_in_path
from odoo import models, _
from collections import OrderedDict
from odoo.tools import config, pdf
from PIL import Image
_logger = logging.getLogger(__name__)


def _get_wkhtmltopdf_bin():
    return find_in_path('wkhtmltopdf')


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def merge_extra_content_pdf(self, res_ids, pdf_content_stream):
        if not res_ids:
            return pdf_content_stream

        content_obj = self.env['report.extra.content']
        model_id = self.env['ir.model'].sudo().search(
            [('model', '=', self.model)])
        res_id = self.env[self.model].browse(res_ids)
        extra_content_id = content_obj.search(
            [('model_id', '=', model_id.id), ('company_id', '=', res_id.company_id.id)])
        custom_documents = []
        if extra_content_id and extra_content_id.append_extra_content:
            main_pdf_fd, main_pdf_path = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.custom.')
            custom_documents.append(main_pdf_path)
            with open(main_pdf_fd, 'wb') as pcd:
                pcd.write(pdf_content_stream.read())

            pdf_custom_fd, pdf_custom_path = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.custom.')
            custom_documents.append(pdf_custom_path)
            with open(pdf_custom_fd, 'wb') as pcd:
                pcd.write(base64.decodebytes(
                    extra_content_id.append_extra_content))

        if custom_documents:
            writer = PdfFileWriter()
            streams = []  # We have to close the streams *after* PdfFilWriter's call to write()
            merged_file_fd, merged_file_path = tempfile.mkstemp(
                suffix='.pdf', prefix='report.merged.tmp.')
            try:
                for document in custom_documents:
                    pdfreport = open(document, 'rb')
                    streams.append(pdfreport)
                    reader = PdfFileReader(pdfreport)
                    for page in range(0, reader.getNumPages()):
                        writer.addPage(reader.getPage(page))

                with closing(os.fdopen(merged_file_fd, 'wb')) as merged_file:
                    writer.write(merged_file)
            finally:
                for stream in streams:
                    try:
                        stream.close()
                    except Exception:
                        pass
            custom_documents.append(merged_file_path)

            with open(merged_file_path, 'rb') as pdf_document:
                pdf_content_stream = pdf_document.read()
            pdf_content_stream = io.BytesIO(pdf_content_stream)

            for temporary_file in custom_documents:
                try:
                    os.unlink(temporary_file)
                except (OSError, IOError):
                    _logger.error(
                        'Error when trying to remove file %s' % temporary_file)

        return pdf_content_stream

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        report_sudo = self._get_report(report_ref)
        report_names = [
            'account.report_invoice',
            'account.report_invoice_with_payments',
            'stock.report_deliveryslip',
            'stock.report_picking',
            'purchase.report_purchaseorder',
            'purchase.report_purchasequotation',
            'sale.report_saleorder',
            'sale.report_saleorder_raw',
        ]
        if report_sudo.report_name in report_names:
            if not data:
                data = {}
            data.setdefault('report_type', 'pdf')

            # access the report details with sudo() but evaluation context as current user
            report_sudo = self._get_report(report_ref)
            collected_streams = OrderedDict()

            # Fetch the existing attachments from the database for later use.
            # Reload the stream from the attachment in case of 'attachment_use'.
            if res_ids:
                records = self.env[report_sudo.model].browse(res_ids)
                for record in records:
                    stream = None
                    attachment = None
                    if report_sudo.attachment:
                        attachment = report_sudo.retrieve_attachment(record)

                        # Extract the stream from the attachment.
                        if attachment and report_sudo.attachment_use:
                            stream = io.BytesIO(attachment.raw)

                            # Ensure the stream can be saved in Image.
                            if attachment.mimetype.startswith('image'):
                                img = Image.open(stream)
                                new_stream = io.BytesIO()
                                img.convert("RGB").save(
                                    new_stream, format="pdf")
                                stream.close()
                                stream = new_stream

                    collected_streams[record.id] = {
                        'stream': stream,
                        'attachment': attachment,
                    }

            # Call 'wkhtmltopdf' to generate the missing streams.
            res_ids_wo_stream = [res_id for res_id, stream_data in collected_streams.items(
            ) if not stream_data['stream']]
            is_whtmltopdf_needed = not res_ids or res_ids_wo_stream

            if is_whtmltopdf_needed:

                if self.get_wkhtmltopdf_state() == 'install':
                    # wkhtmltopdf is not installed
                    # the call should be catched before (cf /report/check_wkhtmltopdf) but
                    # if get_pdf is called manually (email template), the check could be
                    # bypassed
                    raise UserError(
                        _("Unable to find Wkhtmltopdf on this system. The PDF can not be created."))

                # Disable the debug mode in the PDF rendering in order to not split the assets bundle
                # into separated files to load. This is done because of an issue in wkhtmltopdf
                # failing to load the CSS/Javascript resources in time.
                # Without this, the header/footer of the reports randomly disappear
                # because the resources files are not loaded in time.
                # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2083
                additional_context = {'debug': False}

                # As the assets are generated during the same transaction as the rendering of the
                # templates calling them, there is a scenario where the assets are unreachable: when
                # you make a request to read the assets while the transaction creating them is not done.
                # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
                # table.
                # This scenario happens when you want to print a PDF report for the first time, as the
                # assets are not in cache and must be generated. To workaround this issue, we manually
                # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
                if not config['test_enable']:
                    additional_context['commit_assetsbundle'] = True

                html = self.with_context(
                    **additional_context)._render_qweb_html(report_ref, res_ids_wo_stream, data=data)[0]

                bodies, html_ids, header, footer, specific_paperformat_args = self.with_context(
                    **additional_context)._prepare_html(html, report_model=report_sudo.model)

                if report_sudo.attachment and set(res_ids_wo_stream) != set(html_ids):
                    raise UserError(_(
                        "The report's template %r is wrong, please contact your administrator. \n\n"
                        "Can not separate file to save as attachment because the report's template does not contains the"
                        " attributes 'data-oe-model' and 'data-oe-id' on the div with 'article' classname.",
                        self.name,
                    ))
                pdf_content = self._run_wkhtmltopdf(
                    bodies,
                    report_ref=report_ref,
                    header=header,
                    footer=footer,
                    landscape=self._context.get('landscape'),
                    specific_paperformat_args=specific_paperformat_args,
                    set_viewport_size=self._context.get('set_viewport_size'),
                )
                pdf_content_stream = io.BytesIO(pdf_content)

                # Printing a PDF report without any records. The content could be returned directly.
                if not res_ids:
                    return {
                        False: {
                            'stream': pdf_content_stream,
                            'attachment': None,
                        }
                    }
                content_obj = self.env['report.extra.content']
                model_id = self.env['ir.model'].sudo().search(
                    [('model', '=', report_sudo.model)])
                custom_documents = []

                if not report_sudo.attachment:
                    if res_ids:
                        main_pdf_fd, main_pdf_path = tempfile.mkstemp(
                            suffix='.pdf', prefix='report.tmp.custom.')
                        custom_documents.append(main_pdf_path)
                        with open(main_pdf_fd, 'wb') as pcd:
                            pcd.write(pdf_content_stream.read())

                        for res in self.env[report_sudo.model].browse(res_ids):
                            extra_content_id = content_obj.search(
                                [('model_id', '=', model_id.id), ('company_id', '=', res.company_id.id)])
                            if extra_content_id and extra_content_id.append_extra_content:
                                pdf_custom_fd, pdf_custom_path = tempfile.mkstemp(
                                    suffix='.pdf', prefix='report.tmp.custom.')
                                custom_documents.append(pdf_custom_path)
                                with open(pdf_custom_fd, 'wb') as pcd:
                                    pcd.write(base64.decodebytes(
                                        extra_content_id.append_extra_content))
                        if custom_documents:
                            writer = PdfFileWriter()
                            st = []  # We have to close the streams *after* PdfFilWriter's call to write()
                            merged_file_fd, merged_file_path = tempfile.mkstemp(
                                suffix='.pdf', prefix='report.merged.tmp.')
                            try:
                                for document in custom_documents:
                                    pdfreport = open(document, 'rb')
                                    st.append(pdfreport)
                                    reader = PdfFileReader(pdfreport)
                                    for page in range(0, reader.getNumPages()):
                                        writer.addPage(reader.getPage(page))

                                with closing(os.fdopen(merged_file_fd, 'wb')) as merged_file:
                                    writer.write(merged_file)
                            finally:
                                for stt in st:
                                    try:
                                        stt.close()
                                    except Exception:
                                        pass
                            custom_documents.append(merged_file_path)
                            with open(merged_file_path, 'rb') as pdf_document:
                                pdf_content_stream = io.BytesIO(
                                    pdf_document.read())
                    collected_streams[res_ids_wo_stream[0]
                                      ]['stream'] = pdf_content_stream
                    if self._get_report(report_ref).report_name == 'sale.report_saleorder':
                        records = self.env[report_sudo.model].browse(res_ids)
                        for order in records:
                            initial_stream = collected_streams[order.id]['stream']
                            if initial_stream:
                                order_template = order.sale_order_template_id
                                header_record = order_template if order_template.sale_header else order.company_id
                                footer_record = order_template if order_template.sale_footer else order.company_id
                                has_header = bool(header_record.sale_header)
                                has_footer = bool(footer_record.sale_footer)
                                included_product_docs = self.env['product.document']
                                doc_line_id_mapping = {}
                                for line in order.order_line:
                                    product_product_docs = line.product_id.product_document_ids
                                    product_template_docs = line.product_template_id.product_document_ids
                                    doc_to_include = (
                                        product_product_docs.filtered(lambda d: d.attached_on == 'inside')
                                        or product_template_docs.filtered(lambda d: d.attached_on == 'inside')
                                    )
                                    included_product_docs = included_product_docs | doc_to_include
                                    doc_line_id_mapping.update({doc.id: line.id for doc in doc_to_include})

                                if (not has_header and not included_product_docs and not has_footer):
                                    continue

                                writer = PdfFileWriter()
                                if has_header:
                                    self._add_pages_to_writer(writer, base64.b64decode(header_record.sale_header))
                                if included_product_docs:
                                    for doc in included_product_docs:
                                        self._add_pages_to_writer(
                                            writer, base64.b64decode(doc.datas), doc_line_id_mapping[doc.id]
                                        )
                                self._add_pages_to_writer(writer, initial_stream.getvalue())
                                if has_footer:
                                    self._add_pages_to_writer(writer, base64.b64decode(footer_record.sale_footer))

                                form_fields = self._get_form_fields_mapping(order, doc_line_id_mapping)
                                pdf.fill_form_fields_pdf(writer, form_fields=form_fields)
                                with io.BytesIO() as _buffer:
                                    writer.write(_buffer)
                                    stream = io.BytesIO(_buffer.getvalue())
                                collected_streams[order.id].update({'stream': stream})
                        return collected_streams
                    return collected_streams

                # Split the pdf for each record using the PDF outlines.

                # Only one record: append the whole PDF.
                if len(res_ids_wo_stream) == 1:
                    # collected_streams[res_ids_wo_stream[0]]['stream'] = pdf_content_stream
                    # return collected_streams
                    pdf_content_stream = report_sudo.merge_extra_content_pdf(
                        res_ids[0], pdf_content_stream)
                    collected_streams[res_ids_wo_stream[0]
                                      ]['stream'] = pdf_content_stream
                    return collected_streams

                # In case of multiple docs, we need to split the pdf according the records.
                # To do so, we split the pdf based on top outlines computed by wkhtmltopdf.
                # An outline is a <h?> html tag found on the document. To retrieve this table,
                # we look on the pdf structure using pypdf to compute the outlines_pages from
                # the top level heading in /Outlines.
                html_ids_wo_none = [x for x in html_ids if x]
                if len(res_ids_wo_stream) > 1 and set(res_ids_wo_stream) == set(html_ids_wo_none):
                    reader = PdfFileReader(pdf_content_stream)
                    root = reader.trailer['/Root']
                    has_valid_outlines = '/Outlines' in root and '/First' in root['/Outlines']
                    if not has_valid_outlines:
                        return {False: {
                            'report_action': self,
                            'stream': pdf_content_stream,
                            'attachment': None,
                        }}
                    outlines_pages = []
                    node = root['/Outlines']['/First']
                    while True:
                        outlines_pages.append(root['/Dests'][node['/Dest']][0])
                        if '/Next' not in node:
                            break
                        node = node['/Next']
                    outlines_pages = sorted(set(outlines_pages))
                    # The number of outlines must be equal to the number of records to be able to split the document.
                    has_same_number_of_outlines = len(
                        outlines_pages) == len(res_ids)

                    # There should be a top-level heading on first page
                    has_top_level_heading = outlines_pages[0] == 0
                    if has_same_number_of_outlines and has_top_level_heading:
                        # Split the PDF according to outlines.
                        for i, num in enumerate(outlines_pages):
                            to = outlines_pages[i + 1] if i + \
                                1 < len(outlines_pages) else reader.numPages
                            attachment_writer = PdfFileWriter()
                            for j in range(num, to):
                                attachment_writer.addPage(reader.getPage(j))

                                # Append Extra content at last page of pdf report
                                if model_id and res_ids[i]:
                                    res_id = self.env[report_sudo.model].browse(
                                        res_ids[i])
                                    extra_content_id = content_obj.search(
                                        [('model_id', '=', model_id.id), ('company_id', '=', res_id.company_id.id)])
                                    custom_documents = []
                                    if extra_content_id and extra_content_id.append_extra_content:
                                        st = []
                                        pdf_custom_fd, pdf_custom_path = tempfile.mkstemp(
                                            suffix='.pdf', prefix='report.tmp.custom.')
                                        custom_documents.append(
                                            pdf_custom_path)
                                        with open(pdf_custom_fd, 'wb') as pcd:
                                            pcd.write(base64.decodebytes(
                                                extra_content_id.append_extra_content))

                                        ext_pdfreport = open(
                                            pdf_custom_path, 'rb')
                                        st.append(ext_pdfreport)
                                        ext_reader = PdfFileReader(
                                            ext_pdfreport)
                                        for page in range(0, ext_reader.getNumPages()):
                                            attachment_writer.addPage(
                                                ext_reader.getPage(page))

                            stream = io.BytesIO()
                            attachment_writer.write(stream)
                            collected_streams[res_ids[i]]['stream'] = stream

                        return collected_streams

                collected_streams[False] = {
                    'stream': pdf_content_stream, 'attachment': None}

            return collected_streams
        else:
            return super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
