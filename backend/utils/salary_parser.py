"""AI-powered salary slip parser using OpenRouter API"""

import re
import os
import json
from pathlib import Path
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2

# Load environment variables from project root
# The .env file is in the project root, not in backend/
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

print(f"[Salary Parser] Loading .env from: {env_path}")
print(f"[Salary Parser] .env exists: {env_path.exists()}")

# Global client variable
_client = None


def get_openrouter_client():
    """
    Get or create OpenRouter client (lazy initialization)
    
    Returns:
        OpenAI client configured for OpenRouter or None if API key not set
    """
    global _client
    
    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            print("[Salary Parser] ❌ OPENROUTER_API_KEY not set. AI parsing will be disabled.")
            print("[Salary Parser] Please add your API key to the .env file")
            return None
        
        # Check if it's still the placeholder
        if api_key in ["your_openrouter_api_key_here", "your_actual_api_key_here", "<OPENROUTER_API_KEY>"]:
            print("[Salary Parser] ❌ OPENROUTER_API_KEY is still set to placeholder value!")
            print("[Salary Parser] Please replace it with your actual API key from https://openrouter.ai/keys")
            return None
        
        # Mask the key for logging
        masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
        print(f"[Salary Parser] ✅ API Key loaded: {masked_key} (length: {len(api_key)})")
        
        try:
            # Import httpx for custom client configuration
            import httpx
            
            # Create httpx client without proxies parameter
            http_client = httpx.Client(
                timeout=30.0,
                follow_redirects=True
            )
            
            _client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                http_client=http_client
            )
            print("[Salary Parser] ✅ OpenRouter client initialized successfully")
        except Exception as e:
            print(f"[Salary Parser] ❌ Error initializing OpenRouter client: {e}")
            return None
    
    return _client


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
    except Exception as e:
        print(f"[Salary Parser] Error extracting PDF text: {e}")
        return ""


def parse_salary_with_ai(pdf_text: str) -> Optional[dict]:
    """
    Use OpenRouter API to parse salary information from PDF text
    
    Args:
        pdf_text: Extracted text from PDF
        
    Returns:
        Dictionary with parsed salary information or None if parsing fails
    """
    try:
        client = get_openrouter_client()
        if client is None:
            print("[Salary Parser] OpenRouter client not available. Skipping AI parsing.")
            return None
        
        prompt = f"""
Extract the employee name and monthly net salary from the salary slip text below.

Salary Text:
{pdf_text}

Rules:
- Extract the employee/person name as it appears on the slip
- Return only the MONTHLY salary as a NUMBER  
- No commas, no currency symbol in the salary
- If you see annual salary, convert to monthly by dividing by 12
- Look for "Net Salary", "Take Home", or similar monthly amount
- Your final answer MUST be plain JSON:
{{"employee_name": "Full Name", "monthly_salary": number}}
"""
        
        completion = client.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # Check if completion is valid
        if not completion:
            print("[Salary Parser] Error: API returned None completion")
            return None
        
        if not hasattr(completion, 'choices') or not completion.choices:
            print("[Salary Parser] Error: API response has no choices")
            return None
        
        if not completion.choices[0].message:
            print("[Salary Parser] Error: API response has no message")
            return None
        
        response = completion.choices[0].message.content
        
        if not response:
            print("[Salary Parser] Error: API response content is None or empty")
            return None
        
        response = response.strip()
        print(f"[Salary Parser] AI Response: {response}")

        # Clean up response
        if response.startswith("```"):
            response = response.replace("```", "").strip()
            if response.startswith("json"):
                response = response[4:].strip()

        parsed = json.loads(response)

        if "monthly_salary" not in parsed:
            print("[Salary Parser] AI response missing monthly_salary field")
            return None

        monthly_salary = round(float(parsed["monthly_salary"]), 2)
        employee_name = parsed.get("employee_name", "Unknown")
        
        # Validate the salary is reasonable (monthly)
        if monthly_salary < 10000 or monthly_salary > 500000:
            print(f"[Salary Parser] Warning: Monthly salary {monthly_salary} seems unreasonable")
            
            # If it looks like annual, try converting
            if monthly_salary > 500000 and monthly_salary < 6000000:
                print(f"[Salary Parser] Converting from annual to monthly...")
                monthly_salary = round(monthly_salary / 12, 2)
                print(f"[Salary Parser] Adjusted monthly salary: ₹{monthly_salary}")
            else:
                print(f"[Salary Parser] Rejecting AI result")
                return None
        
        # Calculate full salary breakdown from monthly salary
        # Reverse engineer the components
        net_salary = monthly_salary
        
        # Assuming standard deductions (PF 12%, Tax 10% of gross)
        # net = gross - (0.12 * basic) - (0.1 * gross)
        # net = gross - 0.12*basic - 0.1*gross = 0.9*gross - 0.12*basic
        # gross = basic + 0.4*basic + 0.2*basic = 1.6*basic
        # net = 0.9*1.6*basic - 0.12*basic = 1.44*basic - 0.12*basic = 1.32*basic
        # basic = net / 1.32
        
        basic_salary = round(net_salary / 1.32, 2)
        hra = round(basic_salary * 0.4, 2)
        special_allowance = round(basic_salary * 0.2, 2)
        gross_salary = round(basic_salary + hra + special_allowance, 2)
        pf_deduction = round(basic_salary * 0.12, 2)
        tax_deduction = round(gross_salary * 0.1, 2)
        
        print(f"[Salary Parser] Successfully parsed with AI")
        print(f"[Salary Parser] Employee Name: {employee_name}")
        print(f"[Salary Parser] Monthly Salary: ₹{monthly_salary}")
        
        return {
            "employee_name": employee_name,
            "basic_salary": basic_salary,
            "hra": hra,
            "special_allowance": special_allowance,
            "gross_salary": gross_salary,
            "pf_deduction": pf_deduction,
            "tax_deduction": tax_deduction,
            "net_salary": net_salary,
            "monthly_salary": monthly_salary
        }

    except json.JSONDecodeError as e:
        print(f"[Salary Parser] Error parsing JSON response: {e}")
        print(f"[Salary Parser] Response was: {response if 'response' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"[Salary Parser] Error parsing with AI: {e}")
        print(f"[Salary Parser] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

def parse_salary_slip(file_path: str) -> dict:
    """
    Parse salary slip using AI-powered extraction
    
    This function:
    1. Extracts text from the PDF
    2. Uses OpenRouter API (GLM-4.5-air) to intelligently parse salary information
    3. Falls back to filename-based parsing if AI parsing fails
    
    Args:
        file_path: Path to uploaded salary slip PDF
        
    Returns:
        Dictionary with parsed salary information
    """
    file_name = Path(file_path).name.lower()
    
    # Step 1: Extract text from PDF
    print(f"[Salary Parser] Extracting text from PDF: {file_name}")
    pdf_text = extract_text_from_pdf(file_path)
    
    # Debug: Show extracted text sample
    if pdf_text:
        print(f"[Salary Parser] Extracted {len(pdf_text)} characters from PDF")
        print(f"[Salary Parser] Text sample: {pdf_text[:300]}...")
    
    # Step 2: Try AI-powered parsing if we have text
    if pdf_text and len(pdf_text) > 50:  # Ensure we have meaningful content
        print(f"[Salary Parser] Using AI to parse salary information...")
        parsed_data = parse_salary_with_ai(pdf_text)
        
        if parsed_data:
            print(f"[Salary Parser] Successfully parsed with AI. Monthly Salary: ₹{parsed_data['monthly_salary']}")
            return {
                "success": True,
                "parsed_data": parsed_data,
                "confidence": 0.95,
                "extracted_text_sample": pdf_text[:200] + "..." if len(pdf_text) > 200 else pdf_text,
                "method": "ai_powered"
            }
    
    # Step 3: Fallback to filename-based parsing
    print(f"[Salary Parser] AI parsing failed or insufficient text. Falling back to filename-based parsing...")
    
    base_salary = None
    
    # Pattern 1: Look for numbers followed by 'k' (e.g., "50k", "85k")
    salary_match_k = re.search(r'(\d+)k', file_name)
    if salary_match_k:
        base_salary = float(salary_match_k.group(1)) * 1000
        print(f"[Salary Parser] Detected salary from 'Xk' pattern: ₹{base_salary}")
    
    # Pattern 2: Look for larger numbers (likely full salary, e.g., "50000", "85000")
    if not base_salary:
        salary_match_full = re.search(r'(\d{4,6})', file_name)
        if salary_match_full:
            base_salary = float(salary_match_full.group(1))
            print(f"[Salary Parser] Detected salary from full number pattern: ₹{base_salary}")
    
    # Pattern 3: Look for any number (fallback)
    if not base_salary:
        salary_match_any = re.search(r'(\d+)', file_name)
        if salary_match_any:
            num = float(salary_match_any.group(1))
            # If number is small (< 1000), assume it's in thousands
            if num < 1000:
                base_salary = num * 1000
            else:
                base_salary = num
            print(f"[Salary Parser] Detected salary from any number pattern: ₹{base_salary}")
    
    # If still no match, use a default salary
    if not base_salary:
        base_salary = 50000  # Default to 50k instead of random
        print(f"[Salary Parser] No pattern matched, using default salary: ₹{base_salary}")
    
    # Calculate salary breakdown
    hra = base_salary * 0.4
    special_allowance = base_salary * 0.2
    gross_salary = base_salary + hra + special_allowance
    pf = base_salary * 0.12
    tax = gross_salary * 0.1
    net_salary = gross_salary - pf - tax
    
    return {
        "success": True,
        "parsed_data": {
            "basic_salary": round(base_salary, 2),
            "hra": round(hra, 2),
            "special_allowance": round(special_allowance, 2),
            "gross_salary": round(gross_salary, 2),
            "pf_deduction": round(pf, 2),
            "tax_deduction": round(tax, 2),
            "net_salary": round(net_salary, 2),
            "monthly_salary": round(net_salary, 2)
        },
        "confidence": 0.75,
        "extracted_text_sample": f"Fallback parsing from filename: {file_name}",
        "method": "filename_based"
    }


def validate_salary_slip(file_path: str) -> bool:
    """
    Validate if uploaded file is a valid PDF
    
    Args:
        file_path: Path to uploaded file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # Check file extension
    if path.suffix.lower() != '.pdf':
        return False
    
    # Check file size (should be between 10KB and 5MB)
    file_size = path.stat().st_size
    if file_size < 10 * 1024 or file_size > 5 * 1024 * 1024:
        return False
    
    return True

