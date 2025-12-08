"""Sanction Letter Generator Agent"""

from models import Customer, LoanApplication, OfferDetails, SanctionResponse
from utils.sanction_letter_generator import SanctionLetterGenerator
from datetime import datetime
import uuid
import config


class SanctionAgent:
    """
    Sanction Agent responsible for:
    - Generating sanction letter PDF
    - Creating unique sanction ID
    - Providing download link
    """
    
    def __init__(self):
        self.generator = SanctionLetterGenerator()
    
    def generate_sanction_letter(self, customer: Customer, application: LoanApplication,
                                offer: OfferDetails) -> SanctionResponse:
        """
        Generate sanction letter for approved loan
        
        Args:
            customer: Customer profile
            application: Loan application details
            offer: Offer details
            
        Returns:
            SanctionResponse with PDF URL and sanction ID
        """
        # Generate unique sanction ID
        sanction_id = f"SAN{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Prepare application data
        application_data = {
            'application_id': sanction_id,
            'sanction_letter_no': f'SL/2025/{sanction_id}'
        }
        
        # Prepare customer data
        customer_data = {
            'name': customer.name,
            'email': customer.email or 'N/A',
            'phone': customer.phone or 'N/A',
            'address': customer.address or 'N/A'
        }
        
        # Prepare loan details
        loan_details = {
            'amount': offer.amount,
            'interest_rate': offer.interest_rate,
            'tenure': offer.tenure,
            'emi': offer.emi,
            'processing_fee': offer.amount * 0.02  # 2% processing fee
        }
        
        # Generate PDF
        pdf_bytes = self.generator.generate_sanction_letter(
            application_data=application_data,
            customer_data=customer_data,
            loan_details=loan_details
        )
        
        # Save PDF to file
        sanction_filename = f"sanction_{sanction_id}.pdf"
        sanction_path = config.SANCTION_DIR / sanction_filename
        with open(sanction_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Create response
        response = SanctionResponse(
            sanction_id=sanction_id,
            pdf_url=f"/api/sanction/download/{sanction_id}",
            generated_at=datetime.now()
        )
        
        return response
    
    def craft_sanction_message(self, customer: Customer, sanction_id: str,
                              pdf_url: str, offer: OfferDetails) -> str:
        """
        Craft message with sanction letter details
        
        Args:
            customer: Customer profile
            sanction_id: Generated sanction ID
            pdf_url: URL to download PDF
            offer: Offer details
            
        Returns:
            Message with sanction details
        """
        message = f"""
🎊 **Sanction Letter Generated Successfully!** 🎊

Dear {customer.name},

Congratulations! Your loan has been sanctioned. Here are your loan details:

**📄 Sanction ID:** {sanction_id}
**💰 Sanctioned Amount:** Rs. {offer.amount:,.0f}
**⏱️ Tenure:** {offer.tenure} months
**💳 Monthly EMI:** Rs. {offer.emi:,.2f}
**📊 Interest Rate:** {offer.interest_rate}% p.a.

**📥 Download Your Sanction Letter:**
Your official sanction letter is ready! Click the download button below to get your PDF.

**🎯 Next Steps:**
1. Download and review your sanction letter
2. Our team will contact you within 24 hours
3. Complete documentation process
4. Funds will be disbursed within 48 hours

**📞 Need Help?**
Contact us at: 1800-123-4567
Email: support@tatacapital.com

Thank you for choosing Tata Capital! We're excited to serve you. 🙏
""".strip()
        
        return message


# Singleton instance
sanction_agent = SanctionAgent()
