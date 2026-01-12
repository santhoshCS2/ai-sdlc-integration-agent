import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

class DeploymentPDFService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "reports", "deployment")
        os.makedirs(self.output_dir, exist_ok=True)
        self.setup_styles()

    def setup_styles(self):
        self.styles = getSampleStyleSheet()
        
        # Custom Title Style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#2E7D32"), # Green for Deployment
            spaceAfter=20,
            alignment=1 # Center
        ))
        
        # Section Header Style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor("#1B5E20"),
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=5,
            borderWidth=0,
            backColor=colors.HexColor("#E8F5E9")
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
            backColor=colors.HexColor("#F1F8E9"),
            borderPadding=5
        ))

    def generate_report(self, repo_url, strategy_data, file_id):
        """
        Generates a professional PDF report for the deployment strategy.
        """
        filename = f"deployment_strategy_{file_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Header
        story.append(Paragraph("Deployment Strategy & Infrastructure Plan", self.styles['ReportTitle']))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"<b>Repository:</b> {repo_url}", self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Architecture Overview
        story.append(Paragraph("Architecture Overview", self.styles['SectionHeader']))
        story.append(Paragraph(strategy_data.get('architecture_overview', "General microservices architecture."), self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Containerization Strategy
        story.append(Paragraph("Containerization & Docker Strategy", self.styles['SectionHeader']))
        docker_content = strategy_data.get('docker_strategy', "Recommended Docker setup for the project.")
        story.append(Paragraph(docker_content, self.styles['Normal']))
        
        if strategy_data.get('dockerfile_preview'):
            story.append(Paragraph("<b>Proposed Dockerfile:</b>", self.styles['Normal']))
            story.append(Paragraph(f"<code>{strategy_data['dockerfile_preview']}</code>", self.styles['CodeSnippet']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Infrastructure Plan
        story.append(Paragraph("Cloud Infrastructure Plan", self.styles['SectionHeader']))
        infra_content = strategy_data.get('infrastructure_plan', "Cloud deployment recommendations.")
        story.append(Paragraph(infra_content, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # CI/CD Pipeline
        story.append(Paragraph("CI/CD Pipeline Design", self.styles['SectionHeader']))
        cicd_content = strategy_data.get('cicd_pipeline', "CI/CD workflow definitions.")
        story.append(Paragraph(cicd_content, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Deployment Steps Table
        story.append(Paragraph("Sequential Deployment Steps", self.styles['Heading3']))
        steps = strategy_data.get('deployment_steps', [])
        if steps:
            steps_data = [["Step", "Action", "Target Component"]]
            for i, step in enumerate(steps):
                steps_data.append([str(i+1), step.get('action', ''), step.get('component', '')])
            
            t = Table(steps_data, colWidths=[0.5*inch, 3*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C8E6C9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(t)
        
        story.append(PageBreak())
        
        # Monitoring & Scaling
        story.append(Paragraph("Monitoring, Logging & Scaling", self.styles['SectionHeader']))
        mon_content = strategy_data.get('monitoring_strategy', "Scaling and health check strategies.")
        story.append(Paragraph(mon_content, self.styles['Normal']))
        
        doc.build(story)
        logger.info(f"Deployment Report generated: {filepath}")
        return filepath

deployment_pdf_service = DeploymentPDFService()
