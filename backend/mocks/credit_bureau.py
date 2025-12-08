"""Mock Credit Bureau API"""

from typing import Optional
from mocks.crm_service import crm_service


class CreditBureauService:
    """Mock credit bureau service"""
    
    def get_credit_score(self, phone: str) -> Optional[int]:
        """
        Fetch credit score for a customer
        
        In a real system, this would call CIBIL/Experian/Equifax API
        For this mock, we fetch from our customer data
        
        Args:
            phone: Customer's phone number
            
        Returns:
            Credit score (0-900) or None if not found
        """
        customer = crm_service.get_customer_by_phone(phone)
        if customer:
            return customer.credit_score
        return None


# Singleton instance
credit_bureau_service = CreditBureauService()
