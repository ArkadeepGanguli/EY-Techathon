"""
Test script to generate sanction letter for Rajesh Kumar
Based on the approval shown in the UI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sanction_letter_generator import SanctionLetterGenerator
from datetime import datetime

# Initialize generator
generator = SanctionLetterGenerator()

# Data from the screenshot:
# Customer: Rajesh Kumar
# Verified Monthly Salary: ₹46,800.00
# Approved Amount: ₹500,000
# Tenure: 36 months
# EMI: 35.2% of monthly income

# Calculate EMI
monthly_salary = 46800.00
emi_percentage = 0.352
emi = monthly_salary * emi_percentage  # ₹16,473.60

# Prepare application data
application_data = {
    'application_id': 'APP2025001',
    'sanction_letter_no': 'SL/2025/APP2025001'
}

# Prepare customer data
customer_data = {
    'name': 'Rajesh Kumar',
    'email': 'rajesh.kumar@example.com',
    'phone': '+91-9876543210',
    'address': '123, MG Road, Bangalore - 560001, Karnataka, India'
}

# Prepare loan details
loan_details = {
    'amount': 500000,
    'interest_rate': 10.5,
    'tenure': 36,
    'emi': emi,
    'processing_fee': 500000 * 0.02  # 2% processing fee = ₹10,000
}

# Generate PDF
print("🔄 Generating sanction letter for Rajesh Kumar...")
pdf_bytes = generator.generate_sanction_letter(
    application_data=application_data,
    customer_data=customer_data,
    loan_details=loan_details,
    output_path='sanction_letter_rajesh_kumar.pdf'
)

print("✅ Sanction letter generated successfully!")
print(f"📄 File saved as: sanction_letter_rajesh_kumar.pdf")
print(f"📊 Details:")
print(f"   - Customer: {customer_data['name']}")
print(f"   - Loan Amount: ₹{loan_details['amount']:,.2f}")
print(f"   - Tenure: {loan_details['tenure']} months ({loan_details['tenure']//12} years)")
print(f"   - EMI: ₹{loan_details['emi']:,.2f}")
print(f"   - Interest Rate: {loan_details['interest_rate']}% p.a.")
print(f"   - Processing Fee: ₹{loan_details['processing_fee']:,.2f}")
print(f"   - Total Payable: ₹{loan_details['emi'] * loan_details['tenure']:,.2f}")
