"""Underwriting Agent - Risk assessment and loan approval logic"""

from models import Customer, LoanApplication, LoanDecision
from utils.emi_calculator import calculate_emi
import config


class UnderwritingAgent:
    """
    Underwriting Agent responsible for:
    - Credit score evaluation
    - Loan amount vs pre-approved limit comparison
    - EMI to salary ratio calculation
    - Approval/rejection decision with reason codes
    """
    
    def evaluate_loan(self, customer: Customer, requested_amount: float,
                     tenure: int, parsed_salary: float = None) -> dict:
        """
        Evaluate loan application based on underwriting rules
        
        Rules:
        1. Credit score < 700 → Reject
        2. Amount ≤ pre-approved limit → Instant Approval
        3. Amount ≤ 2× pre-approved limit:
           - Request salary slip
           - EMI must be ≤ 50% of monthly salary
        4. Amount > 2× pre-approved limit → Reject
        
        Args:
            customer: Customer profile
            requested_amount: Requested loan amount
            tenure: Loan tenure in months
            parsed_salary: Parsed salary from slip (if uploaded)
            
        Returns:
            Dictionary with decision, reason, and reason code
        """
        # Rule 1: Check credit score
        if customer.credit_score < config.MIN_CREDIT_SCORE:
            return {
                "decision": LoanDecision.REJECTED,
                "reason": f"Your credit score ({customer.credit_score}) is below our minimum requirement of {config.MIN_CREDIT_SCORE}.",
                "reason_code": "LOW_CREDIT_SCORE",
                "message": self._craft_rejection_message(customer, "credit_score")
            }
        
        # Rule 2: Check if within pre-approved limit
        if requested_amount <= customer.pre_approved_limit:
            return {
                "decision": LoanDecision.APPROVED,
                "reason": "Loan amount is within pre-approved limit.",
                "reason_code": "PRE_APPROVED",
                "message": self._craft_approval_message(customer, requested_amount, tenure)
            }
        
        # Rule 3: Check if within 2x pre-approved limit
        if requested_amount <= customer.pre_approved_limit * config.PRE_APPROVED_MULTIPLIER:
            # Need salary verification
            if parsed_salary is None:
                return {
                    "decision": LoanDecision.CONDITIONAL,
                    "reason": f"Loan amount (₹{requested_amount:,.0f}) exceeds pre-approved limit (₹{customer.pre_approved_limit:,.0f}). Salary verification required.",
                    "reason_code": "SALARY_VERIFICATION_REQUIRED",
                    "message": self._craft_conditional_message(customer, requested_amount)
                }
            
            # Check EMI to salary ratio
            from utils.emi_calculator import get_interest_rate
            interest_rate = get_interest_rate(customer.credit_score)
            emi = calculate_emi(requested_amount, interest_rate, tenure)
            emi_ratio = emi / parsed_salary
            
            if emi_ratio <= config.MAX_EMI_TO_SALARY_RATIO:
                return {
                    "decision": LoanDecision.APPROVED,
                    "reason": f"EMI (₹{emi:,.2f}) is {emi_ratio*100:.1f}% of salary, within acceptable limit.",
                    "reason_code": "APPROVED_WITH_SALARY_VERIFICATION",
                    "emi_ratio": emi_ratio,
                    "message": self._craft_approval_message(customer, requested_amount, tenure, emi_ratio)
                }
            else:
                return {
                    "decision": LoanDecision.REJECTED,
                    "reason": f"EMI (₹{emi:,.2f}) is {emi_ratio*100:.1f}% of your salary, exceeding our maximum limit of {config.MAX_EMI_TO_SALARY_RATIO*100}%.",
                    "reason_code": "HIGH_EMI_TO_SALARY_RATIO",
                    "emi_ratio": emi_ratio,
                    "message": self._craft_rejection_message(customer, "emi_ratio", emi, parsed_salary, emi_ratio)
                }
        
        # Rule 4: Amount exceeds 2x pre-approved limit
        else:
            return {
                "decision": LoanDecision.REJECTED,
                "reason": f"Requested amount (₹{requested_amount:,.0f}) exceeds maximum eligible amount (₹{customer.pre_approved_limit * config.PRE_APPROVED_MULTIPLIER:,.0f}).",
                "reason_code": "AMOUNT_EXCEEDS_LIMIT",
                "message": self._craft_rejection_message(customer, "amount_exceeded", requested_amount, customer.pre_approved_limit * config.PRE_APPROVED_MULTIPLIER)
            }
    
    def _craft_approval_message(self, customer: Customer, amount: float, 
                               tenure: int, emi_ratio: float = None) -> str:
        """Craft approval message"""
        
        if emi_ratio:
            ratio_text = f"\n• Your EMI is {emi_ratio*100:.1f}% of your monthly income - well within safe limits!"
        else:
            ratio_text = ""
        
        message = f"""
🎉 **Congratulations, {customer.name}!** 🎉

**Your loan has been APPROVED!** ✅

**Approved Amount:** Rs. {amount:,.0f}
**Tenure:** {tenure} months{ratio_text}

You're just one step away from getting your funds. Let me generate your sanction letter now...
""".strip()
        
        return message
    
    def _craft_rejection_message(self, customer: Customer, reason_type: str, 
                                *args) -> str:
        """Craft rejection message"""
        
        if reason_type == "credit_score":
            message = f"""
😔 **Loan Application Status: Not Approved**

Dear {customer.name},

Unfortunately, we're unable to approve your loan application at this time.

**Reason:** Your credit score ({customer.credit_score}) is below our minimum requirement of {config.MIN_CREDIT_SCORE}.

**💡 What you can do:**
• Work on improving your credit score by:
  - Paying existing EMIs on time
  - Reducing credit card utilization
  - Clearing any overdue payments
• Reapply after 6 months

We're here to help you in your financial journey. For any queries, contact us at 1800-123-4567.
""".strip()
        
        elif reason_type == "emi_ratio":
            emi, salary, ratio = args
            message = f"""
😔 **Loan Application Status: Not Approved**

Dear {customer.name},

After careful evaluation, we're unable to approve your loan application.

**Reason:** The monthly EMI (₹{emi:,.2f}) would be {ratio*100:.1f}% of your monthly salary (₹{salary:,.2f}), which exceeds our safe lending limit of {config.MAX_EMI_TO_SALARY_RATIO*100}%.

**💡 Suggestions:**
• Consider a lower loan amount
• Choose a longer tenure to reduce EMI
• You can reapply with updated income documents

For assistance, contact us at 1800-123-4567.
""".strip()
        
        elif reason_type == "amount_exceeded":
            requested, max_eligible = args
            message = f"""
😔 **Loan Application Status: Not Approved**

Dear {customer.name},

We're unable to approve the requested loan amount.

**Requested Amount:** ₹{requested:,.0f}
**Maximum Eligible Amount:** ₹{max_eligible:,.0f}

**💡 Options:**
• Apply for ₹{max_eligible:,.0f} or less
• Build your credit history and reapply later

We appreciate your interest. Contact us at 1800-123-4567 for more information.
""".strip()
        
        else:
            message = f"Unfortunately, we're unable to approve your loan application at this time. Please contact our support team."
        
        return message
    
    def _craft_conditional_message(self, customer: Customer, amount: float) -> str:
        """Craft message for conditional approval"""
        
        message = f"""
📋 **Additional Verification Required**

Hi {customer.name},

Your requested amount of ₹{amount:,.0f} exceeds your pre-approved limit of ₹{customer.pre_approved_limit:,.0f}.

**Good news:** You may still be eligible! We just need to verify your income.

I'll need your salary slip to proceed with the evaluation.
""".strip()
        
        return message


# Singleton instance
underwriting_agent = UnderwritingAgent()
