import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from xml.sax.saxutils import escape
import logging

logger = logging.getLogger(__name__)

class TestingPDFService:
    def __init__(self, output_dir: str = "generated_reports/testing"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.colors = {
            'primary': HexColor('#2E86AB'),
            'secondary': HexColor('#A23B72'),
            'success': HexColor('#28A745'),
            'warning': HexColor('#FFC107'),
            'danger': HexColor('#DC3545'),
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
        self.styles.add(ParagraphStyle(name='CustomBullet', parent=self.styles['Normal'], fontSize=10, spaceAfter=4, leftIndent=20, textColor=self.colors['text']))
        self.styles.add(ParagraphStyle(name='StatsLabel', parent=self.styles['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=self.colors['text']))
        self.styles.add(ParagraphStyle(name='PassText', parent=self.styles['Normal'], fontSize=10, textColor=self.colors['success'], fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='FailText', parent=self.styles['Normal'], fontSize=10, textColor=self.colors['danger'], fontName='Helvetica-Bold'))

    def _sanitize(self, text):
        if not text: return ""
        return escape(str(text))

    def generate_report(self, repo_url: str, test_results: dict, file_id: str) -> str:
        """Generate professional PDF report for testing results"""
        output_path = os.path.join(self.output_dir, f"testing_report_{file_id}.pdf")
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Title Page
        elements.append(Paragraph("Comprehensive Testing Report", self.styles['CustomTitle']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['CustomBody']))
        elements.append(Paragraph(f"Repository: {self._sanitize(repo_url)}", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.5 * inch))

        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['CustomHeading1']))
        
        stats = test_results.get('statistics', {})
        total_tests = stats.get('total_tests', 0)
        passed_tests = stats.get('passed', 0)
        failed_tests = stats.get('failed', 0)
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary_text = f"The automated testing suite executed <b>{total_tests}</b> test cases. "
        summary_text += f"Achievement: <b>{passed_tests}</b> passed ({pass_rate:.1f}%) and <b>{failed_tests}</b> failed."
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))

        # Statistics Table
        elements.append(Paragraph("Test Execution Statistics", self.styles['CustomHeading2']))
        data = [
            ['Metric', 'Count'],
            ['Total Tests', str(total_tests)],
            ['Passed', str(passed_tests)],
            ['Failed', str(failed_tests)],
            ['Code Files Analyzed', str(stats.get('code_files', 0))],
            ['Test Files Generated', str(stats.get('test_files', 0))]
        ]
        
        t = Table(data, colWidths=[3*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['light_gray']),
            ('GRID', (0, 0), (-1, -1), 1, white),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.5 * inch))

        # Detailed Test Cases
        if 'test_cases' in test_results and test_results['test_cases']:
            elements.append(PageBreak())
            elements.append(Paragraph("Detailed Test Cases", self.styles['CustomHeading1']))
            
            for test_file, tests in test_results['test_cases'].items():
                elements.append(Paragraph(f"File: {self._sanitize(test_file)}", self.styles['CustomHeading2']))
                
                for test in tests:
                    status_style = self.styles['PassText'] if test.get('status', 'passed') == 'passed' else self.styles['FailText']
                    elements.append(Paragraph(f"• {self._sanitize(test.get('name', 'Unknown Test'))}: {test.get('status', 'unknown')}", status_style))
                    if test.get('error'):
                         elements.append(Paragraph(f"  Error: {self._sanitize(test['error'])}", self.styles['CustomBody']))
                
                elements.append(Spacer(1, 0.1 * inch))

        # Final Footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph("Report generated by ANTIGRAVITE AI Testing Agent.", self.styles['CustomBody']))

        doc.build(elements)
        logger.info(f"Generated PDF report: {output_path}")
        return output_path

testing_pdf_service = TestingPDFService()
