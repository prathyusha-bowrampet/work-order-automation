from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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

        # Page layout
        self.PAGE_HEIGHT = A4[1]
        self.PAGE_WIDTH = A4[0]
        self.PAGE_Margin = 2.54 * cm

        # Set default paragraph
        self.styles = getSampleStyleSheet()
        self.styles['Normal'].fontName = 'BaiJamjuree'                          # Base Font
        self.styles['Normal'].fontSize = 11                                     # Font size
        self.styles['Normal'].leading = self.styles['Normal'].fontSize * 1.5    # Line spacing
        self.styles['Normal'].spaceAfter = self.styles['Normal'].fontSize       # Gap after paragraph
        # Set default paragraph
        self.styles = getSampleStyleSheet()
        self.styles['title'].fontName = 'BaiJamjuree'                          # Base Font
        self.styles['title'].fontSize = 12                                     # Font size
        self.styles['title'].leading = self.styles['Normal'].fontSize * 1.5    # Line spacing
        self.styles['title'].spaceAfter = self.styles['Normal'].fontSize       # Gap after paragraph
        self.styles['title'].textColor = colors.rgb2cmyk(0, (111 / 255), (192 / 255))

    def make_page(self, summery, workorder):
        doc = SimpleDocTemplate("test.pdf",
                                pagesize=A4,
                                topMargin=self.PAGE_Margin,
                                leftMargin=self.PAGE_Margin,
                                rightMargin=self.PAGE_Margin,
                                bottomMargin=self.PAGE_Margin)
        story = [Paragraph(summery, self.styles["title"])]
        for bogustext in workorder:
            p = Paragraph(bogustext, self.styles["Normal"])
            story.append(p)

        doc.build(story)
