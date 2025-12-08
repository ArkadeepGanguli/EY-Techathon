"""Sales Agent - Handles offer presentation and negotiation"""

from models import Customer, LoanApplication, OfferDetails, ConversationMemory
from utils.emi_calculator import calculate_emi, calculate_total_payable, get_interest_rate
from mocks.offer_mart import offer_mart_service
import config


class SalesAgent:
    """
    Sales Agent responsible for:
    - Presenting pre-approved offers
    - Negotiating interest rate, tenure, amount
    - Handling objections
    - Maximizing conversion probability
    """
    
    def present_offer(self, customer: Customer, requested_amount: float, 
                     requested_tenure: int) -> dict:
        """
        Present loan offer to customer
        
        Args:
            customer: Customer profile
            requested_amount: Requested loan amount
            requested_tenure: Requested tenure in months
            
        Returns:
            Dictionary with offer presentation message and details
        """
        # Get interest rate based on credit score
        interest_rate = get_interest_rate(customer.credit_score)
        
        # Calculate EMI
        emi = calculate_emi(requested_amount, interest_rate, requested_tenure)
        total_payable = calculate_total_payable(emi, requested_tenure)
        
        # Get offer details from offer mart
        offers = offer_mart_service.get_offers(customer.id, customer.credit_score)
        
        # Create offer details
        offer = OfferDetails(
            amount=requested_amount,
            tenure=requested_tenure,
            interest_rate=interest_rate,
            emi=emi,
            total_payable=total_payable
        )
        
        # Craft persuasive message
        message = self._craft_offer_message(customer, offer, offers)
        
        return {
            "message": message,
            "offer": offer,
            "offers_data": offers
        }
    
    def _craft_offer_message(self, customer: Customer, offer: OfferDetails, 
                            offers_data: dict) -> str:
        """Craft a persuasive offer presentation message"""
        
        # Determine credit score category
        if customer.credit_score >= 800:
            credit_category = "excellent"
            rate_message = "🌟 Congratulations! Your excellent credit score qualifies you for our **best interest rate**!"
        elif customer.credit_score >= 750:
            credit_category = "good"
            rate_message = "✨ Great news! Your good credit score qualifies you for a **competitive interest rate**!"
        else:
            credit_category = "fair"
            rate_message = "👍 You qualify for our personal loan with a fair interest rate."
        
        message = f"""
{rate_message}

**📋 Your Personalized Loan Offer:**

💰 **Loan Amount:** ₹{offer.amount:,.0f}
⏱️ **Tenure:** {offer.tenure} months ({offer.tenure//12} years)
📊 **Interest Rate:** {offer.interest_rate}% per annum
💳 **Monthly EMI:** ₹{offer.emi:,.2f}
📈 **Total Payable:** ₹{offer.total_payable:,.2f}

**✅ Key Benefits:**
• Instant approval for pre-approved customers
• Flexible repayment options
• No hidden charges
• Quick disbursement within 24-48 hours

**💡 Processing Fee:** {offers_data['processing_fee_percent']}% + GST (deducted from loan amount)

Would you like to proceed with this offer? You can also choose a different tenure if you prefer.
""".strip()
        
        return message
    
    def handle_tenure_change(self, customer: Customer, amount: float, 
                           new_tenure: int) -> dict:
        """
        Handle customer request to change tenure
        
        Args:
            customer: Customer profile
            amount: Loan amount
            new_tenure: New requested tenure
            
        Returns:
            Updated offer details
        """
        if new_tenure not in config.TENURE_OPTIONS:
            return {
                "success": False,
                "message": f"Sorry, {new_tenure} months is not a valid tenure option. Please choose from: {', '.join(map(str, config.TENURE_OPTIONS))} months."
            }
        
        # Recalculate with new tenure
        interest_rate = get_interest_rate(customer.credit_score)
        emi = calculate_emi(amount, interest_rate, new_tenure)
        total_payable = calculate_total_payable(emi, new_tenure)
        
        message = f"""
**Updated Offer with {new_tenure} months tenure:**

💳 **Monthly EMI:** ₹{emi:,.2f}
📈 **Total Payable:** ₹{total_payable:,.2f}

This looks good! Shall we proceed with this?
""".strip()
        
        return {
            "success": True,
            "message": message,
            "emi": emi,
            "total_payable": total_payable
        }
    
    def handle_objection(self, objection_type: str, customer: Customer, 
                        amount: float, tenure: int) -> str:
        """
        Handle customer objections with persuasive responses
        
        Args:
            objection_type: Type of objection (high_emi, high_rate, etc.)
            customer: Customer profile
            amount: Loan amount
            tenure: Tenure in months
            
        Returns:
            Persuasive response message
        """
        if objection_type == "high_emi":
            # Suggest longer tenure
            longer_tenure = min([t for t in config.TENURE_OPTIONS if t > tenure], default=tenure)
            if longer_tenure > tenure:
                interest_rate = get_interest_rate(customer.credit_score)
                new_emi = calculate_emi(amount, interest_rate, longer_tenure)
                return f"""
I understand your concern about the EMI. Let me offer you a more comfortable option:

If we extend the tenure to **{longer_tenure} months**, your EMI would reduce to just **₹{new_emi:,.2f}** per month.

This gives you more breathing room in your monthly budget. Would this work better for you?
""".strip()
            else:
                return "I understand. The current tenure is already at maximum. Would you like to consider a lower loan amount?"
        
        elif objection_type == "high_rate":
            return f"""
I appreciate your concern. The interest rate of **{get_interest_rate(customer.credit_score)}%** is based on your credit score of **{customer.credit_score}**.

This is actually a competitive rate in the market for personal loans. Plus, you get:
✅ No collateral required
✅ Quick disbursement
✅ Flexible prepayment options

Would you like to proceed? The rate is locked for you right now!
""".strip()
        
        else:
            return "I understand your concern. Let me know how I can help make this work for you!"


# Singleton instance
sales_agent = SalesAgent()
