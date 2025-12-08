"""Mock Offer Mart service"""

from typing import List, Dict
from utils.emi_calculator import get_interest_rate
import config


class OfferMartService:
    """Mock offer mart service to fetch loan offers"""
    
    def get_offers(self, customer_id: str, credit_score: int) -> Dict:
        """
        Get available loan offers for a customer
        
        Args:
            customer_id: Customer's ID
            credit_score: Customer's credit score
            
        Returns:
            Dictionary with offer details
        """
        interest_rate = get_interest_rate(credit_score)
        
        return {
            "customer_id": customer_id,
            "interest_rate": interest_rate,
            "tenure_options": config.TENURE_OPTIONS,
            "processing_fee_percent": 2.0,
            "prepayment_charges": {
                "within_12_months": 4.0,
                "after_12_months": 2.0
            },
            "features": [
                "Instant approval for pre-approved customers",
                "Flexible tenure options",
                "No hidden charges",
                "Quick disbursement"
            ]
        }


# Singleton instance
offer_mart_service = OfferMartService()
