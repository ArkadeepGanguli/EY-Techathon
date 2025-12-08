"""Verification Agent - Handles KYC and document verification"""

from models import Customer
from pathlib import Path
import config


class VerificationAgent:
    """
    Verification Agent responsible for:
    - Performing KYC verification
    - Confirming phone, address, identity
    - Simulating OTP verification
    - Accepting and validating salary slip uploads
    """
    
    def verify_kyc(self, customer: Customer) -> dict:
        """
        Verify KYC status of customer
        
        Args:
            customer: Customer profile
            
        Returns:
            Dictionary with verification status and message
        """
        if customer.kyc_status == "verified":
            message = f"""
✅ **KYC Verification Complete**

Your identity has been verified successfully:
• **Name:** {customer.name}
• **Phone:** {customer.phone}
• **Address:** {customer.address}
• **KYC Status:** Verified ✓

We're all set to proceed with your loan application!
""".strip()
            return {
                "success": True,
                "verified": True,
                "message": message
            }
        
        elif customer.kyc_status == "pending":
            message = f"""
⚠️ **KYC Verification Pending**

Hi {customer.name}, we need to complete your KYC verification first.

For this demo, I'm simulating an OTP verification...

**📱 OTP Sent to {customer.phone}**

Please confirm: Did you receive the OTP? (In this demo, any response will verify you)
""".strip()
            return {
                "success": True,
                "verified": False,
                "requires_otp": True,
                "message": message
            }
        
        else:  # failed
            message = f"""
❌ **KYC Verification Failed**

Unfortunately, we couldn't verify your KYC details. Please contact our support team at 1800-123-4567 for assistance.
""".strip()
            return {
                "success": False,
                "verified": False,
                "message": message
            }
    
    def simulate_otp_verification(self, customer: Customer) -> dict:
        """
        Simulate OTP verification (always succeeds in demo)
        
        Args:
            customer: Customer profile
            
        Returns:
            Verification result
        """
        message = f"""
✅ **OTP Verified Successfully!**

Thank you, {customer.name}. Your phone number has been verified.

Your KYC is now complete. Let's proceed with your loan application!
""".strip()
        
        return {
            "success": True,
            "verified": True,
            "message": message
        }
    
    def request_salary_slip(self, customer: Customer, reason: str = "") -> str:
        """
        Request salary slip upload from customer
        
        Args:
            customer: Customer profile
            reason: Reason for requesting salary slip
            
        Returns:
            Request message
        """
        if reason:
            reason_text = f"\n\n**Reason:** {reason}"
        else:
            reason_text = ""
        
        message = f"""
📄 **Salary Slip Required**

Hi {customer.name}, to process your loan application, we need to verify your income.{reason_text}

**Please upload your latest salary slip (PDF format):**
• Should be from the last 3 months
• Must be a clear, readable PDF
• File size: 10KB - 5MB

Once you upload, I'll verify it instantly!
""".strip()
        
        return message
    
    def validate_uploaded_file(self, filename: str, file_size: int) -> dict:
        """
        Validate uploaded salary slip file
        
        Args:
            filename: Name of uploaded file
            file_size: Size of file in bytes
            
        Returns:
            Validation result
        """
        # Check file extension
        if not filename.lower().endswith('.pdf'):
            return {
                "success": False,
                "message": "❌ Please upload a PDF file only. Other formats are not accepted."
            }
        
        # Check file size (10KB - 5MB)
        if file_size < 10 * 1024:
            return {
                "success": False,
                "message": "❌ File is too small. Please upload a valid salary slip PDF."
            }
        
        if file_size > 5 * 1024 * 1024:
            return {
                "success": False,
                "message": "❌ File is too large. Please upload a file smaller than 5MB."
            }
        
        return {
            "success": True,
            "message": "✅ File validated successfully. Processing your salary slip..."
        }
    
    def confirm_salary_verification(self, parsed_salary: float, customer_name: str) -> str:
        """
        Confirm salary verification after parsing
        
        Args:
            parsed_salary: Parsed monthly salary
            customer_name: Customer's name
            
        Returns:
            Confirmation message
        """
        message = f"""
✅ **Salary Slip Verified Successfully!**

Thank you, {customer_name}. I've verified your salary slip.

**Verified Monthly Salary:** ₹{parsed_salary:,.2f}

Now let me check your loan eligibility based on this income...
""".strip()
        
        return message


# Singleton instance
verification_agent = VerificationAgent()
