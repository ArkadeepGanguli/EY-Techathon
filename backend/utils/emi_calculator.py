"""EMI calculation utilities"""

import math


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate EMI using the standard formula:
    EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    
    Where:
    P = Principal loan amount
    r = Monthly interest rate (annual rate / 12 / 100)
    n = Tenure in months
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (percentage)
        tenure_months: Loan tenure in months
        
    Returns:
        Monthly EMI amount
    """
    if principal <= 0 or annual_rate <= 0 or tenure_months <= 0:
        return 0.0
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / 12 / 100
    
    # Calculate EMI
    numerator = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
    denominator = math.pow(1 + monthly_rate, tenure_months) - 1
    
    emi = numerator / denominator
    
    return round(emi, 2)


def calculate_total_payable(emi: float, tenure_months: int) -> float:
    """Calculate total amount payable over the loan tenure"""
    return round(emi * tenure_months, 2)


def get_interest_rate(credit_score: int) -> float:
    """
    Get interest rate based on credit score
    
    Args:
        credit_score: Customer's credit score
        
    Returns:
        Annual interest rate percentage
    """
    if credit_score >= 800:
        return 10.5  # Excellent
    elif credit_score >= 750:
        return 11.5  # Good
    elif credit_score >= 700:
        return 12.5  # Fair
    else:
        return 13.5  # Below threshold
