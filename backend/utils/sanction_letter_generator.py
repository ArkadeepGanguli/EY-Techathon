"""
Sanction Letter Generator Service
Generates professional PDF loan sanction letters
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY
from datetime import datetime, timedelta
from typing import Dict, Any
import io


class SanctionLetterGenerator:
    """Generate professional loan sanction letters in PDF format"""
    
    def __init__(self):
        self.company_name = "Tata Capital Limited"
        self.company_address = "11th Floor, Tower A, Peninsula Business Park\nGanpatrao Kadam Marg, Lower Parel\nMumbai - 400013, Maharashtra, India"
        self.company_email = "customercare@tatacapital.com"
        self.company_phone = "1800-209-6464"
        self.company_website = "www.tatacapital.com"
    
    def generate_sanction_letter(
        self,
        application_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        loan_details: Dict[str, Any],
        output_path: str = None
    ) -> bytes:
        """
        Generate complete sanction letter PDF
        
        Args:
            application_data: Application ID, date, etc.
            customer_data: Customer name, address, etc.
            loan_details: Loan amount, tenure, EMI, etc.
            output_path: Optional file path to save PDF
        
        Returns:
            PDF bytes
        """
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
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
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Add company letterhead
        elements.extend(self._create_letterhead())
        
        # Add title
        elements.append(Spacer(1, 0.3*inch))
        title = Paragraph("LOAN SANCTION LETTER", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add reference details
        ref_data = [
            ['Sanction Letter No:', application_data.get('sanction_letter_no', 'SL/2025/'+application_data['application_id'])],
            ['Date:', datetime.now().strftime('%d %B %Y')],
            ['Application ID:', application_data['application_id']]
        ]
        
        ref_table = Table(ref_data, colWidths=[2*inch, 4*inch])
        ref_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(ref_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer details
        customer_text = f"""
        <b>To,</b><br/>
        <b>{customer_data['name']}</b><br/>
        {customer_data.get('address', 'N/A')}<br/>
        Email: {customer_data.get('email', 'N/A')}<br/>
        Phone: {customer_data.get('phone', 'N/A')}
        """
        elements.append(Paragraph(customer_text, normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Subject
        subject_style = ParagraphStyle(
            'Subject',
            parent=normal_style,
            fontName='Helvetica-Bold'
        )
        subject = Paragraph(
            f"<b>Subject: Sanction of Personal Loan - Rs. {loan_details['amount']:,.2f}</b>",
            subject_style
        )
        elements.append(subject)
        elements.append(Spacer(1, 0.2*inch))
        
        # Opening paragraph
        opening = f"""
        Dear {customer_data['name'].split()[0]},<br/><br/>
        We are pleased to inform you that your application for a Personal Loan has been 
        <b>approved</b> by {self.company_name}. The sanction is subject to the terms and 
        conditions mentioned herein.
        """
        elements.append(Paragraph(opening, normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Loan details table
        elements.append(Paragraph("<b>LOAN DETAILS</b>", heading_style))
        
        # Calculate values
        total_repayment = loan_details['emi'] * loan_details['tenure']
        total_interest = total_repayment - loan_details['amount']
        processing_fee = loan_details.get('processing_fee', loan_details['amount'] * 0.02)
        disbursement_amount = loan_details['amount'] - processing_fee
        
        loan_data = [
            ['Loan Amount Sanctioned', f"Rs. {loan_details['amount']:,.2f}"],
            ['Interest Rate (per annum)', f"{loan_details['interest_rate']}%"],
            ['Loan Tenure', f"{loan_details['tenure']} months ({loan_details['tenure']//12} years)"],
            ['Monthly EMI', f"Rs. {loan_details['emi']:,.2f}"],
            ['Processing Fee', f"Rs. {processing_fee:,.2f}"],
            ['Net Disbursement Amount', f"Rs. {disbursement_amount:,.2f}"],
            ['Total Amount Payable', f"Rs. {total_repayment:,.2f}"],
            ['Total Interest Payable', f"Rs. {total_interest:,.2f}"],
            ['EMI Start Date', loan_details.get('emi_start_date', (datetime.now() + timedelta(days=30)).strftime('%d %B %Y'))],
            ['Loan Maturity Date', loan_details.get('maturity_date', (datetime.now() + timedelta(days=30*loan_details['tenure'])).strftime('%d %B %Y'))]
        ]
        
        loan_table = Table(loan_data, colWidths=[3*inch, 2.5*inch])
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(loan_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Terms and conditions
        elements.append(Paragraph("<b>TERMS AND CONDITIONS</b>", heading_style))
        
        terms = [
            "The loan is subject to verification of all documents submitted by you.",
            "EMI payments must be made on or before the due date each month through auto-debit from your bank account.",
            "The interest rate is fixed for the entire tenure of the loan.",
            "Processing fee is non-refundable and will be deducted from the loan amount at the time of disbursement.",
            "You may prepay the loan at any time subject to prepayment charges as per our policy.",
            "In case of default in EMI payment, penal interest will be charged as per our policy.",
            "The loan is provided for personal use and cannot be used for speculative or illegal purposes.",
            "You must maintain adequate insurance coverage as per our requirements.",
            "Any change in your employment status or residential address must be intimated to us immediately.",
            "This sanction is valid for 30 days from the date of this letter."
        ]
        
        for i, term in enumerate(terms, 1):
            term_para = Paragraph(f"{i}. {term}", normal_style)
            elements.append(term_para)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Documents required
        elements.append(Paragraph("<b>DOCUMENTS REQUIRED FOR DISBURSEMENT</b>", heading_style))
        
        docs_text = """
        1. Duly signed loan agreement<br/>
        2. Post-dated cheques (PDCs) for EMI payments<br/>
        3. Bank account details for disbursement<br/>
        4. Latest salary slip (if not already submitted)<br/>
        5. Address proof and identity proof (KYC documents)<br/>
        6. Any other documents as communicated by our loan officer
        """
        elements.append(Paragraph(docs_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Closing
        closing_text = """
        We appreciate your trust in our services and look forward to a long-lasting relationship. 
        For any queries or assistance, please feel free to contact our customer care team.
        """
        elements.append(Paragraph(closing_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Signature
        signature_text = """
        <b>For Tata Capital Limited</b><br/><br/><br/>
        <b>Authorized Signatory</b><br/>
        Credit Manager<br/>
        Personal Loans Division
        """
        elements.append(Paragraph(signature_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer note
        footer_style = ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer_text = f"""
        <i>This is a computer-generated document and does not require a physical signature.</i><br/>
        <b>{self.company_name}</b> | {self.company_phone} | {self.company_email} | {self.company_website}
        """
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _create_letterhead(self):
        """Create company letterhead"""
        elements = []
        
        # Company name
        title_style = ParagraphStyle(
            'CompanyName',
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        company_name = Paragraph(self.company_name.upper(), title_style)
        elements.append(company_name)
        
        # Company details
        detail_style = ParagraphStyle(
            'CompanyDetails',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        details = Paragraph(
            f"{self.company_address.replace(chr(10), '<br/>')}<br/>"
            f"Phone: {self.company_phone} | Email: {self.company_email} | Website: {self.company_website}",
            detail_style
        )
        elements.append(details)
        
        # Horizontal line
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1a237e')),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.grey),
        ]))
        elements.append(line_table)
        
        return elements


# FastAPI endpoint integration
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

class SanctionLetterRequest(BaseModel):
    application_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    customer_address: str
    loan_amount: float
    interest_rate: float
    tenure: int
    emi: float
    processing_fee: float = None


@app.post("/api/generate-sanction-letter")
async def generate_sanction_letter_endpoint(request: SanctionLetterRequest):
    """
    Generate and download sanction letter PDF
    """
    try:
        generator = SanctionLetterGenerator()
        
        # Prepare data
        application_data = {
            'application_id': request.application_id,
            'sanction_letter_no': f'SL/2025/{request.application_id}'
        }
        
        customer_data = {
            'name': request.customer_name,
            'email': request.customer_email,
            'phone': request.customer_phone,
            'address': request.customer_address
        }
        
        loan_details = {
            'amount': request.loan_amount,
            'interest_rate': request.interest_rate,
            'tenure': request.tenure,
            'emi': request.emi,
            'processing_fee': request.processing_fee or (request.loan_amount * 0.02)
        }
        
        # Generate PDF
        pdf_bytes = generator.generate_sanction_letter(
            application_data=application_data,
            customer_data=customer_data,
            loan_details=loan_details
        )
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=sanction_letter_{request.application_id}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Standalone usage example
if __name__ == "__main__":
    generator = SanctionLetterGenerator()
    
    # Sample data
    application_data = {
        'application_id': 'APP001',
        'sanction_letter_no': 'SL/2025/APP001'
    }
    
    customer_data = {
        'name': 'Rakesh Kumar',
        'email': 'rakesh.kumar@example.com',
        'phone': '+91-9876543210',
        'address': 'Flat 201, Green Valley Apartments, Sector V, Salt Lake City, Kolkata - 700091, West Bengal, India'
    }
    
    loan_details = {
        'amount': 400000,
        'interest_rate': 10.5,
        'tenure': 48,
        'emi': 10151.47
    }
    
    # Generate PDF
    pdf_bytes = generator.generate_sanction_letter(
        application_data=application_data,
        customer_data=customer_data,
        loan_details=loan_details,
        output_path='sanction_letter_sample.pdf'
    )
    
    print("✅ Sanction letter generated successfully!")
    print("📄 File: sanction_letter_sample.pdf")