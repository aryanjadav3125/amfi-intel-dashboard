import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

class PDFGenerator:
    """
    Generates analyst-grade PDF reports for Mutual Funds.
    """
    def __init__(self, output_dir: str = "reports_output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_fund_report(self, fund_data: dict, filename: str) -> str:
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = styles['Heading1']
        title_style.alignment = 1 # Center
        
        heading_style = styles['Heading2']
        heading_style.textColor = colors.HexColor("#1e3a8a")
        
        normal_style = styles['Normal']
        
        elements = []
        
        # 1. Cover / Title
        elements.append(Paragraph(f"<b>{fund_data.get('name', 'Fund Report')}</b>", title_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Category: {fund_data.get('category', 'N/A')}", normal_style))
        elements.append(Paragraph(f"AMC: {fund_data.get('amc', 'N/A')}", normal_style))
        elements.append(Spacer(1, 24))
        
        # 2. Executive Summary
        elements.append(Paragraph("Executive Summary", heading_style))
        elements.append(Spacer(1, 6))
        
        summary_data = [
            ["Latest NAV", str(fund_data.get('nav', 'N/A'))],
            ["1Y CAGR", f"{fund_data.get('cagr_1y', 'N/A')}%"],
            ["5Y CAGR", f"{fund_data.get('cagr_5y', 'N/A')}%"],
            ["Riskometer", fund_data.get('risk', 'N/A')]
        ]
        
        t = Table(summary_data, colWidths=[150, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))
        
        # 3. Top Holdings
        elements.append(Paragraph("Top Holdings", heading_style))
        elements.append(Spacer(1, 6))
        
        holdings = fund_data.get('holdings', [])
        if holdings:
            holdings_table_data = [["Company", "Sector", "Allocation %"]]
            for h in holdings[:10]: # Top 10
                holdings_table_data.append([h['company'], h['sector'], f"{h['allocation']}%"])
                
            t2 = Table(holdings_table_data, colWidths=[200, 150, 100])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ]))
            elements.append(t2)
        else:
            elements.append(Paragraph("No holdings data available.", normal_style))
            
        # Build PDF
        doc.build(elements)
        return filepath
