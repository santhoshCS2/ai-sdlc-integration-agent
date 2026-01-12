import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

class SecurityPDFService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "reports", "security")
        os.makedirs(self.output_dir, exist_ok=True)
        self.setup_styles()

    def setup_styles(self):
        self.styles = getSampleStyleSheet()
        
        # Custom Title Style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#1A237E"), # Deep Blue
            spaceAfter=20,
            alignment=1 # Center
        ))
        
        # Section Header Style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor("#1A237E"),
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=5,
            borderWidth=0,
            backColor=colors.HexColor("#E8EAF6")
        ))
        
        # Critical Issue Style
        self.styles.add(ParagraphStyle(
            name='CriticalIssue',
            parent=self.styles['Normal'],
            textColor=colors.red,
            fontWeight='BOLD'
        ))
        
        # Code Snippet Style
        self.styles.add(ParagraphStyle(
            name='CodeSnippet',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=5,
            spaceAfter=5,
            backColor=colors.HexColor("#F5F5F5"),
            borderPadding=5
        ))

    def generate_report(self, repo_url, report_data, file_id):
        """
        Generates a professional PDF report from technical scan data.
        """
        filename = f"security_report_{file_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Header
        story.append(Paragraph("Security & Quality Analysis Report", self.styles['ReportTitle']))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"<b>Repository:</b> {repo_url}", self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        summary_text = report_data.get('executive_summary', "A comprehensive security scan was performed.")
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Key Metrics Table
        metrics = report_data.get('metrics', {})
        story.append(Paragraph("Platform Metrics", self.styles['Heading3']))
        
        metrics_data = [
            ["Metric", "Value", "Status"],
            ["Overall Security Score", f"{metrics.get('security_score', 0)}/100", self._get_status(metrics.get('security_score', 0))],
            ["Code Quality Score", f"{metrics.get('quality_score', 0)}/100", self._get_status(metrics.get('quality_score', 0))],
            ["Risk Level", metrics.get('risk_level', 'UNKNOWN'), metrics.get('risk_level', 'UNKNOWN')],
            ["Compliance Status", metrics.get('compliance_status', 'N/A'), metrics.get('compliance_status', 'N/A')]
        ]
        
        t = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#CFD8DC")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3 * inch))
        
        # Detailed Findings
        story.append(Paragraph("Critical Vulnerabilities & Findings", self.styles['SectionHeader']))
        
        issues = report_data.get('raw_data', {}).get('issues', [])
        # Sort issues by severity
        severity_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        issues.sort(key=lambda x: severity_map.get(x.get('severity', 'LOW'), 99))
        
        if not issues:
            story.append(Paragraph("✅ No critical vulnerabilities detected in this scan.", self.styles['Normal']))
        else:
            for issue in issues[:20]: # Limit to top 20 for report readability
                severity = issue.get('severity', 'INFO').upper()
                story.append(Paragraph(f"<b>[{severity}]</b> {issue.get('file', 'Unknown')}:{issue.get('line', '?')}", 
                                      self.styles['Normal'] if severity != 'CRITICAL' else self.styles['CriticalIssue']))
                story.append(Paragraph(issue.get('issue', 'No description provided'), self.styles['Normal']))
                
                if issue.get('code_snippet'):
                    story.append(Paragraph(f"<code>{issue['code_snippet']}</code>", self.styles['CodeSnippet']))
                
                if issue.get('minimal_fix', {}).get('suggestion'):
                    story.append(Paragraph(f"<i>Recommendation: {issue['minimal_fix']['suggestion']}</i>", self.styles['Normal']))
                
                story.append(Spacer(1, 0.1 * inch))

        story.append(PageBreak())
        
        # Recommendations
        story.append(Paragraph("Actionable Recommendations", self.styles['SectionHeader']))
        recs = report_data.get('recommendations', [])
        if not recs:
            story.append(Paragraph("Continue maintaining best security practices.", self.styles['Normal']))
        else:
            for rec in recs:
                story.append(Paragraph(f"<b>• {rec['title']} ({rec['priority']})</b>", self.styles['Normal']))
                story.append(Paragraph(rec['description'], self.styles['Normal']))
                story.append(Spacer(1, 0.05 * inch))

        doc.build(story)
        logger.info(f"Report generated: {filepath}")
        return filepath

    def _get_status(self, score):
        if score >= 80: return "HEALTHY"
        if score >= 50: return "WARNING"
        return "CRITICAL"

security_pdf_service = SecurityPDFService()
