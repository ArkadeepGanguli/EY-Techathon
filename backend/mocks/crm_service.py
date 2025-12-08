"""Mock CRM service"""

import json
from pathlib import Path
from typing import Optional
from models import Customer
import config


class CRMService:
    """Mock CRM service to fetch customer data"""
    
    def __init__(self):
        """Load customer data from mock JSON file"""
        with open(config.MOCK_DATA_PATH, 'r') as f:
            data = json.load(f)
            self.customers = {c['phone']: Customer(**c) for c in data['customers']}
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """
        Fetch customer profile by phone number
        
        Args:
            phone: Customer's phone number
            
        Returns:
            Customer object if found, None otherwise
        """
        return self.customers.get(phone)
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        Fetch customer profile by customer ID
        
        Args:
            customer_id: Customer's ID
            
        Returns:
            Customer object if found, None otherwise
        """
        for customer in self.customers.values():
            if customer.id == customer_id:
                return customer
        return None


# Singleton instance
crm_service = CRMService()
