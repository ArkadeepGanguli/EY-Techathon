"""Sanction letter PDF generator"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
from pathlib import Path
import config


def generate_sanction_letter(sanction_id: str, customer_name: str, customer_address: str,
                            loan_amount: float, tenure: int, interest_rate: float,
                            emi: float, total_payable: float) -> str:
    """
    Generate a professional sanction letter PDF
    
    Args:
        sanction_id: Unique sanction ID
        customer_name: Customer's name
        customer_address: Customer's address
        loan_amount: Sanctioned loan amount
        tenure: Loan tenure in months
        interest_rate: Annual interest rate
        emi: Monthly EMI amount
        total_payable: Total amount to be repaid
        
    Returns:
        Path to generated PDF file
    """
    # Create filename
    filename = f"sanction_{sanction_id}.pdf"
    filepath = config.SANCTION_DIR / filename
    
    # Create PDF document
    doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    # Header
    header_data = [
        [Paragraph("<b>TATA CAPITAL FINANCIAL SERVICES LIMITED</b>", 
                   ParagraphStyle('HeaderCompany', parent=styles['Normal'], 
                                fontSize=14, textColor=colors.HexColor('#1a237e'),
                                alignment=TA_CENTER, fontName='Helvetica-Bold'))],
        [Paragraph("Corporate Office: Mumbai, Maharashtra", 
                   ParagraphStyle('HeaderAddress', parent=styles['Normal'], 
                                fontSize=9, alignment=TA_CENTER))],
    ]
    
    header_table = Table(header_data, colWidths=[6.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Title
    elements.append(Paragraph("LOAN SANCTION LETTER", title_style))
    
    # Reference details
    ref_date = datetime.now().strftime("%d %B, %Y")
    elements.append(Paragraph(f"<b>Sanction ID:</b> {sanction_id}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {ref_date}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Customer details
    elements.append(Paragraph("CUSTOMER DETAILS", heading_style))
    elements.append(Paragraph(f"<b>Name:</b> {customer_name}", normal_style))
    elements.append(Paragraph(f"<b>Address:</b> {customer_address}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Loan details
    elements.append(Paragraph("LOAN SANCTION DETAILS", heading_style))
    
    loan_data = [
        ['Particulars', 'Details'],
        ['Sanctioned Loan Amount', f'₹ {loan_amount:,.2f}'],
        ['Tenure', f'{tenure} months ({tenure//12} years)'],
        ['Interest Rate (Annual)', f'{interest_rate}% p.a.'],
        ['Monthly EMI', f'₹ {emi:,.2f}'],
        ['Total Amount Payable', f'₹ {total_payable:,.2f}'],
    ]
    
    loan_table = Table(loan_data, colWidths=[3*inch, 3*inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(loan_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Terms and conditions
    elements.append(Paragraph("TERMS & CONDITIONS", heading_style))
    
    terms = [
        "1. This sanction is valid for 30 days from the date of issue.",
        "2. Disbursement is subject to completion of documentation and verification.",
        "3. Processing fee of 2% + GST will be deducted from the loan amount.",
        "4. EMI will be auto-debited from your registered bank account on the 5th of every month.",
        "5. Prepayment charges: 4% on the outstanding principal if prepaid within 12 months.",
        "6. Late payment charges of ₹500 + 2% per month will apply on overdue EMIs.",
        "7. The loan is subject to the terms and conditions mentioned in the loan agreement.",
    ]
    
    for term in terms:
        elements.append(Paragraph(term, normal_style))
        elements.append(Spacer(1, 0.05*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Congratulations message
    congrats_style = ParagraphStyle(
        'Congrats',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2e7d32'),
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Congratulations on your loan approval!", congrats_style))
    elements.append(Paragraph("Our team will contact you shortly to complete the documentation.", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("For queries, contact us at: 1800-123-4567 | support@tatacapital.com", footer_style))
    elements.append(Paragraph("This is a system-generated document and does not require a signature.", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    return str(filepath)
