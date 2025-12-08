"""__init__.py for mocks package"""

from .crm_service import crm_service
from .credit_bureau import credit_bureau_service
from .offer_mart import offer_mart_service

__all__ = ['crm_service', 'credit_bureau_service', 'offer_mart_service']
