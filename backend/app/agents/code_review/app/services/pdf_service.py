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

class CodeReviewPDFService:
    def __init__(self, output_dir: str = "generated_reports/code_review"):
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
        self.styles.add(ParagraphStyle(name='GitHubCode', parent=self.styles['Normal'], fontSize=8, fontName='Courier', textColor=self.colors['text'], backColor=self.colors['light_gray'], leftIndent=10, rightIndent=10, spaceAfter=4))
        self.styles.add(ParagraphStyle(name='DiffAdd', parent=self.styles['Normal'], fontSize=8, fontName='Courier', textColor=self.colors['success'], backColor=HexColor('#E6FFED'), leftIndent=10, rightIndent=10))
        self.styles.add(ParagraphStyle(name='DiffRemove', parent=self.styles['Normal'], fontSize=8, fontName='Courier', textColor=self.colors['danger'], backColor=HexColor('#FFEEDD'), leftIndent=10, rightIndent=10))

    def _sanitize(self, text):
        if not text: return ""
        return escape(str(text))

    def generate_report(self, repo_url: str, updated_url: str, changes: list, file_id: str) -> str:
        """Generate professional PDF report for code review fixes"""
        output_path = os.path.join(self.output_dir, f"code_review_{file_id}.pdf")
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Title Page
        elements.append(Paragraph("Automated Code Review Report", self.styles['CustomTitle']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.5 * inch))

        # Project Info
        elements.append(Paragraph("Project Information", self.styles['CustomHeading1']))
        elements.append(Paragraph(f"<b>Original Repository:</b> {self._sanitize(repo_url)}", self.styles['CustomBody']))
        elements.append(Paragraph(f"<b>Updated Repository:</b> {self._sanitize(updated_url)}", self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))

        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['CustomHeading1']))
        total_files = len(changes)
        total_lines = sum(c.get('total_lines_changed', 0) for c in changes)
        summary_text = f"This automated code review successfully identified and fixed issues in <b>{total_files}</b> files, resulting in <b>{total_lines}</b> total line modifications. The fixes addressed security vulnerabilities, code quality issues, and performance optimizations."
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3 * inch))

        # Detailed Changes
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Fixes & Optimizations", self.styles['CustomHeading1']))

        for change in changes:
            elements.append(Paragraph(f"File: {self._sanitize(change['file'])}", self.styles['CustomHeading2']))
            
            # Issues Fixed
            elements.append(Paragraph("Issues Fixed:", self.styles['CustomBody']))
            for issue in change.get('issues_fixed', []):
                elements.append(Paragraph(f"• {self._sanitize(issue)}", self.styles['CustomBullet']))
            
            # Explanation
            elements.append(Paragraph(f"<b>Fix Explanation:</b> {self._sanitize(change.get('fix_explanation', 'N/A'))}", self.styles['CustomBody']))
            
            # Optimizations
            if change.get('optimizations'):
                elements.append(Paragraph("AI Optimizations Applying:", self.styles['CustomBody']))
                for opt in change['optimizations']:
                    elements.append(Paragraph(f"• {self._sanitize(opt)}", self.styles['CustomBullet']))

            # Diff View (Simplified)
            elements.append(Paragraph("Change Visualization:", self.styles['CustomBody']))
            for lc in change.get('line_changes', [])[:20]: # Show first 20 changes per file
                line_num = lc.get('line_number', 0)
                if lc['change_type'] == 'modified':
                    elements.append(Paragraph(f"L{line_num}: - {self._sanitize(lc['original'])}", self.styles['DiffRemove']))
                    elements.append(Paragraph(f"L{line_num}: + {self._sanitize(lc['fixed'])}", self.styles['DiffAdd']))
                elif lc['change_type'] == 'added':
                    elements.append(Paragraph(f"L{line_num}: + {self._sanitize(lc['fixed'])}", self.styles['DiffAdd']))
                elif lc['change_type'] == 'removed':
                    elements.append(Paragraph(f"L{line_num}: - {self._sanitize(lc['original'])}", self.styles['DiffRemove']))
            
            if len(change.get('line_changes', [])) > 20:
                elements.append(Paragraph(f"... and {len(change['line_changes']) - 20} more changes", self.styles['CustomBody']))
            
            elements.append(Spacer(1, 0.2 * inch))

        # Final Footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph("Report generated by ANTIGRAVITE AI Code Review Agent.", self.styles['CustomBody']))

        doc.build(elements)
        logger.info(f"Generated PDF report: {output_path}")
        return output_path

code_review_pdf_service = CodeReviewPDFService()
