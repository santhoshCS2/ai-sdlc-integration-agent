import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from xml.sax.saxutils import escape
import logging

logger = logging.getLogger(__name__)

class ImpactPDFService:
    def __init__(self, output_dir: str = "generated_reports/impact"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.colors = {
            'primary': HexColor('#2E86AB'),
            'secondary': HexColor('#A23B72'),
            'accent': HexColor('#F39C12'),
            'text': HexColor('#2D3748'),
            'light_gray': HexColor('#F7FAFC'),
            'medium_gray': HexColor('#E2E8F0'),
        }
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(name='CustomTitle', parent=self.styles['Title'], fontSize=24, spaceAfter=30, textColor=self.colors['primary'], alignment=TA_CENTER, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='CustomHeading1', parent=self.styles['Heading1'], fontSize=18, spaceAfter=12, spaceBefore=20, textColor=self.colors['primary'], fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='CustomHeading2', parent=self.styles['Heading2'], fontSize=14, spaceAfter=10, spaceBefore=15, textColor=self.colors['secondary'], fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='CustomBody', parent=self.styles['Normal'], fontSize=10, spaceAfter=6, textColor=self.colors['text'], alignment=TA_JUSTIFY))
        self.styles.add(ParagraphStyle(name='MetricLabel', parent=self.styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=self.colors['text']))
        self.styles.add(ParagraphStyle(name='MetricValue', parent=self.styles['Normal'], fontSize=11, textColor=self.colors['primary']))

    def _sanitize(self, text):
        if not text: return ""
        # Handle double newlines for paragraphs
        text = str(text).replace('\n\n', '<br/><br/>').replace('\n', ' ')
        return escape(text).replace('&lt;br/&gt;', '<br/>')

    def generate_report(self, repo_url: str, impact_content: str, file_id: str) -> str:
        """Generate professional PDF report for impact analysis"""
        output_path = os.path.join(self.output_dir, f"impact_report_{file_id}.pdf")
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        elements = []

        # Title Page
        elements.append(Paragraph("Business & Technical Impact Analysis", self.styles['CustomTitle']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['CustomBody']))
        elements.append(Paragraph(f"Project Repository: {repo_url if repo_url else 'N/A'}", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.5 * inch))

        # Executive Summary Table
        elements.append(Paragraph("Strategic Overview", self.styles['CustomHeading1']))
        data = [
            ['Category', 'Strategic Assessment'],
            ['Business Impact', 'Analysis of market position and ROI potential.'],
            ['Technical Complexity', 'Evaluation of architectural challenges.'],
            ['Risk Profile', 'Identification of critical path dependencies.']
        ]
        
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['light_gray']),
            ('GRID', (0, 0), (-1, -1), 1, white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.4 * inch))

        # Main Content
        # Split content into sections if they look like markdown headers
        sections = impact_content.split('\n#')
        for i, section in enumerate(sections):
            if not section.strip(): continue
            
            lines = section.strip().split('\n')
            title = lines[0].strip('# ').strip()
            content = '\n'.join(lines[1:]).strip()
            
            if i > 0: # Already has a title if split by #
                elements.append(Paragraph(title, self.styles['CustomHeading1']))
            
            # Process sub-sections or paragraphs
            sub_sections = content.split('\n## ')
            for sub in sub_sections:
                if not sub.strip(): continue
                sub_lines = sub.strip().split('\n')
                if len(sub_lines) > 1 and not sub.startswith(' '):
                    sub_title = sub_lines[0].strip()
                    sub_content = '\n'.join(sub_lines[1:]).strip()
                    elements.append(Paragraph(sub_title, self.styles['CustomHeading2']))
                    elements.append(Paragraph(self._sanitize(sub_content), self.styles['CustomBody']))
                else:
                    elements.append(Paragraph(self._sanitize(sub), self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.2 * inch))

        # Final Footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph("Report generated by ANTIGRAVITE AI Business & Technical Impact Agent.", self.styles['CustomBody']))

        doc.build(elements)
        logger.info(f"Generated Impact PDF: {output_path}")
        return os.path.abspath(output_path)

impact_pdf_service = ImpactPDFService()
