"""
Example script to test the AI-powered salary parser

This script demonstrates how to use the new OpenRouter API integration
to parse salary information from PDF files.
"""

import sys
import os

# Add parent directory to path to import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.salary_parser import parse_salary_slip, validate_salary_slip


def test_salary_parser(pdf_path: str):
    """
    Test the salary parser with a given PDF file
    
    Args:
        pdf_path: Path to the PDF file to parse
    """
    print("=" * 80)
    print("AI-Powered Salary Parser Test")
    print("=" * 80)
    print(f"\nTesting with file: {pdf_path}\n")
    
    # Validate the file first
    print("Step 1: Validating PDF file...")
    if not validate_salary_slip(pdf_path):
        print("❌ File validation failed!")
        print("   - Check if file exists")
        print("   - Check if file is a PDF")
        print("   - Check if file size is between 10KB and 5MB")
        return
    
    print("✅ File validation passed!\n")
    
    # Parse the salary slip
    print("Step 2: Parsing salary information...")
    result = parse_salary_slip(pdf_path)
    
    print("\n" + "=" * 80)
    print("PARSING RESULTS")
    print("=" * 80)
    
    if result["success"]:
        print(f"\n✅ Parsing successful!")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Confidence: {result['confidence'] * 100}%")
        
        print("\n📊 Salary Breakdown:")
        print("-" * 80)
        
        data = result["parsed_data"]
        print(f"   Basic Salary:        ₹{data['basic_salary']:>12,.2f}")
        print(f"   HRA:                 ₹{data['hra']:>12,.2f}")
        print(f"   Special Allowance:   ₹{data['special_allowance']:>12,.2f}")
        print(f"   {'─' * 45}")
        print(f"   Gross Salary:        ₹{data['gross_salary']:>12,.2f}")
        print(f"\n   Deductions:")
        print(f"   PF Deduction:        ₹{data['pf_deduction']:>12,.2f}")
        print(f"   Tax Deduction:       ₹{data['tax_deduction']:>12,.2f}")
        print(f"   {'─' * 45}")
        print(f"   Net Salary:          ₹{data['net_salary']:>12,.2f}")
        print(f"   Monthly Salary:      ₹{data['monthly_salary']:>12,.2f}")
        
        print("\n📄 Extracted Text Sample:")
        print("-" * 80)
        sample = result.get("extracted_text_sample", "N/A")
        print(f"   {sample[:200]}...")
        
    else:
        print("\n❌ Parsing failed!")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        # Use provided file path
        pdf_file = sys.argv[1]
    else:
        # Use a default test file (you can change this)
        pdf_file = "test_salary_slip.pdf"
        print(f"No file specified. Using default: {pdf_file}")
        print("Usage: python test_salary_parser.py <path_to_pdf>\n")
    
    # Check if file exists
    if not os.path.exists(pdf_file):
        print(f"❌ Error: File '{pdf_file}' not found!")
        print("\nTo test the parser:")
        print("1. Create or download a salary slip PDF")
        print("2. Run: python test_salary_parser.py path/to/your/salary_slip.pdf")
        sys.exit(1)
    
    # Run the test
    test_salary_parser(pdf_file)
