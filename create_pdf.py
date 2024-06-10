from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from shapely import from_wkt

import io
import logging


class CreatePDF:
    def __init__(self):
        # Add SNO Font
        pdfmetrics.registerFont(TTFont('BaiJamjuree', 'BaiJamjuree-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('BaiJamjureeBd', 'BaiJamjuree-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('BaiJamjureeIt', 'BaiJamjuree-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('BaiJamjureeBI', 'BaiJamjuree-BoldItalic.ttf'))
        pdfmetrics.registerFontFamily('BaiJamjuree',
                                      normal='BaiJamjuree',
                                      bold='BaiJamjureeBd',
                                      italic='BaiJamjureeIt',
                                      boldItalic='BaiJamjureeBI')
        self.page_title = "<b>{type}</b> – {fg} ({fc})"
        self.midspan_template = """<b>{a_end}</b> Egress duct length: <b>{length}</b> Lat/Long: <b>{a_end_lat:.6f}, {a_end_long:.6f}</b><br/>
Label ingress duct: <b>{ingress_label}</b><br/>
Label egress duct: <b>{egress_label}</b>"""

        self.workorder_start = """{type} feeder required<br/>
from: {cab_ring}Chamber {a_end} Lat/Long {a_lat:.6f}, {a_long:.6f}<br/> 
to: {cab_blank}Chamber {b_end} Lat/Long {b_lat:.6f}, {b_long:.6f}<br/>
"""

        # Page layout
        self.PAGE_HEIGHT = A4[1]
        self.PAGE_WIDTH = A4[0]
        self.PAGE_Margin = 2.54 * cm
        self.SNO_BLUE = colors.rgb2cmyk(0, (111 / 255), (192 / 255))

        # Set default paragraph
        self.styles = getSampleStyleSheet()
        self.styles['Normal'].fontName = 'BaiJamjuree'                          # Base Font
        self.styles['Normal'].fontSize = 11                                     # Font size
        self.styles['Normal'].leading = self.styles['Normal'].fontSize * 1.5    # Line spacing
        self.styles['Normal'].spaceAfter = self.styles['Normal'].fontSize       # Gap after paragraph

        # Set default paragraph
        self.styles['title'].fontName = 'BaiJamjuree'                          # Base Font
        self.styles['title'].fontSize = 12                                     # Font size
        self.styles['title'].leading = self.styles['Normal'].fontSize * 1.5    # Line spacing
        self.styles['title'].spaceAfter = self.styles['Normal'].fontSize       # Gap after paragraph
        self.styles['title'].textColor = self.SNO_BLUE


    def make_page(self, workorder, wo_type):
        story = []
        bytes_file_obj = io.BytesIO()
        doc = SimpleDocTemplate(bytes_file_obj,
                                pagesize=A4,
                                topMargin=self.PAGE_Margin,
                                leftMargin=self.PAGE_Margin,
                                rightMargin=self.PAGE_Margin,
                                bottomMargin=self.PAGE_Margin)
        if wo_type == 'Feeder Stage 1':
            story = [Paragraph(self.page_title.format(type=wo_type, fg=workorder.fg, fc=workorder.fc),
                               self.styles["title"])]

            aend = workorder.get_a_chamber()
            bend = workorder.get_b_chamber()
            if aend and bend:
                aend_point = from_wkt(aend['WKT'])
                bend_point = from_wkt(bend['WKT'])
            else:
                return False

            data = [["Order ID", ""],
                    ["Project ID", workorder.city],
                    ["Start Point", "{} Lat/Long: {:.6f}, {:.6f}".format(workorder.a_end,
                                                                         aend_point.y,
                                                                         aend_point.x)],
                    ["End Point", "{} Lat/Long: {:.6f}, {:.6f}".format(workorder.b_end,
                                                                       bend_point.y,
                                                                       bend_point.x)],
                    ["Approximate cable length (Feet)", workorder.length],
                    ["Approximate cable length with loops (Feet)", workorder.length_inc_loops()],
                    ["Required number of gas seals", workorder.num_seals()],
                    ["Required number of couplers", workorder.num_couplers()]]
            table_summary = Table(data)
            table_summary.setStyle(TableStyle([('TEXTCOLOR', (0, 0), (0, -1), self.SNO_BLUE)]))

            story.append(Spacer(self.PAGE_WIDTH, self.styles['Normal'].fontSize))

            story.append(table_summary)

            story.append(Spacer(self.PAGE_WIDTH, self.styles['Normal'].fontSize))

            fc_num = workorder.fc.split('-')
            fg_num = workorder.fg.split('-')

            story.append(Paragraph("Notify SNO that the work is starting by emailing noc@snonetops.com quoting the work order reference number.",
                                   self.styles["Normal"]))

            story.append(Paragraph("Any issues or discrepancies with this work order, please also contact the NOC at SNO (657) 217-2970) to address this issue and ensure that it is resolved to optimise delivery of the work order.",
                                   self.styles["Normal"]))

            story.append(Paragraph("### START OF WORK ORDER ###",
                                   self.styles["Normal"]))
            cab_ring = ''
            cab_blank = ''
            if workorder.feeder_type.upper() == "BRANCH":
                cab_ring = 'Ring '
            else:
                cab_ring = 'Cab '
                cab_blank = 'Cab '



            story.append(Paragraph(self.workorder_start.format(type=workorder.feeder_type,
                                                               cab_ring=cab_ring,
                                                               a_lat=aend_point.y,
                                                               a_long=aend_point.x,
                                                               b_lat=bend_point.y,
                                                               b_long=bend_point.x,
                                                               cab_blank=cab_blank,
                                                               a_end=workorder.a_end,
                                                               b_end=workorder.b_end),
                                   self.styles["Normal"]))


            for chamber in workorder.chambers:
                chamber_point = from_wkt(chamber['WKT'])
                a_lat = chamber_point.y
                a_long = chamber_point.x
                seg_template = "FC-{fc} FG-{fg} FS-{fs} A-CH-{a_ch} B-CH-{b_ch}"
                ingess_seg = "None"
                egress_seg = "None"
                length = "N/A"
                for seg in workorder.segs:
                    if seg['AEnd'] == chamber['ID']:
                        fs_num = seg['ID'].split('-')
                        a_num = seg['AEnd'].split('-', 2)
                        b_num = seg['BEnd'].split('-', 2)
                        if seg['LengthFt'] == "N/A":
                            length = seg['LengthFt']
                        else:
                            length = "{} Ft".format(seg['LengthFt'])
                        ingess_seg = seg_template.format(fc=fc_num[2],
                                                         fg=fg_num[2],
                                                         fs=fs_num[2],
                                                         a_ch=a_num[2],
                                                         b_ch=b_num[2])

                    if seg['BEnd'] == chamber['ID']:
                        fs_num = seg["ID"].split('-')
                        a_num = seg["AEnd"].split('-', 2)
                        b_num = seg['BEnd'].split('-', 2)
                        egress_seg = seg_template.format(fc=fc_num[2],
                                                         fg=fg_num[2],
                                                         fs=fs_num[2],
                                                         a_ch=a_num[2],
                                                         b_ch=b_num[2])

                p = Paragraph(self.midspan_template.format(a_end=chamber['ID'],
                                                           length=length,
                                                           a_end_lat=a_lat,
                                                           a_end_long=a_long,
                                                           ingress_label=egress_seg,
                                                           egress_label=ingess_seg),
                              self.styles["Normal"])
                story.append(p)

            story.append(Paragraph("Before installing the fiber at each mid-point chamber fit duct couplers to enable the fiber to be blown.",
                                   self.styles["Normal"]))

            story.append(Paragraph("After installing the fiber, remove most of the duct that the fiber is in, within the chamber and ensure 30ft of fiber is coiled within the chamber before fitting gas seals to each section of duct the fiber passes through.",
                                   self.styles["Normal"]))

            story.append(Paragraph("Take geo-tagged photograph of the labelling of the fiber and gas seals. Shape file of the path attached to the Service Desk (Jira) ticket.",
                                   self.styles["Normal"]))

            story.append(Paragraph("### END OF WORK ORDER ###",
                                   self.styles["Normal"]))

            story.append(Paragraph("Upon completion of a feeder network stage 1 work order (fiber blowing) Arcadis will be required to perform QA/QC of the fiber install, which will include:",
                                   self.styles["Normal"]))

            story.append(Paragraph("Visual inspection of the chambers the fiber is required to be present at and confirm no visible damage to the fiber.",
                                   self.styles["Normal"]))

            story.append(Paragraph("Confirm fiber is correctly labelled in accordance with the work order requirements Confirm gas seals have been fitted to 16/12mm metro duct around fiber.",
                                   self.styles["Normal"]))
            story.append(Paragraph("Take geo-tagged photograph of the labelling of the fiber and gas seals. Photograph fiber within the chambers",
                                   self.styles["Normal"]))
            story.append(Paragraph("Notify SNO that the work is complete by calling (657) 217-2970 quoting the work order number.",
                                   self.styles["Normal"]))
            story.append(Paragraph("Upload the photographs to the Service Desk (Jira) Work Order ticket created and referenced by SNO.",
                                   self.styles["Normal"]))
            story.append(Paragraph("Once reviewed by SNO, SNO will close the ticket.",
                                   self.styles["Normal"]))
        doc.build(story)

        bytes_file_obj.seek(0)
        return bytes_file_obj

