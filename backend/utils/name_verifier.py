"""
Name Verification Utility using OpenRouter API
Compares customer name with name extracted from salary slip
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL', 'http://localhost:3000')
OPENROUTER_SITE_NAME = os.getenv('OPENROUTER_SITE_NAME', 'EY Techathon Loan System')


def verify_names_match(customer_name: str, salary_slip_name: str) -> dict:
    """
    Verify if two names match using OpenRouter AI
    
    Args:
        customer_name: Name from CRM/customer profile
        salary_slip_name: Name extracted from salary slip
        
    Returns:
        dict with keys:
            - match: bool - True if names likely belong to same person
            - confidence: float - Confidence score (0-1)
            - reason: str - Explanation of the decision
    """
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == 'sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
        print("[Name Verification] WARNING: OpenRouter API key not configured")
        # Fallback to simple string comparison
        return {
            'match': customer_name.lower().strip() == salary_slip_name.lower().strip(),
            'confidence': 1.0 if customer_name.lower().strip() == salary_slip_name.lower().strip() else 0.0,
            'reason': 'Simple string comparison (API key not configured)'
        }
    
    try:
        print(f"[Name Verification] Comparing:")
        print(f"  Customer Name: '{customer_name}'")
        print(f"  Salary Slip Name: '{salary_slip_name}'")
        
        prompt = f"""You are a name matching expert. Compare these two names and determine if they likely belong to the same person.

Customer Name (from CRM): "{customer_name}"
Salary Slip Name (from document): "{salary_slip_name}"

Consider:
- Different name orders (First Last vs Last First)
- Middle names or initials
- Abbreviated names
- Common spelling variations
- Nicknames vs formal names

IMPORTANT: Respond ONLY with valid JSON in this exact format (no markdown, no code blocks, no extra text):
{{
    "match": true,
    "confidence": 0.95,
    "reason": "brief explanation"
}}"""

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": OPENROUTER_SITE_URL,
                "X-Title": OPENROUTER_SITE_NAME,
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.3-70b-instruct:free",  # Reliable free model
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 200
            },
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract the AI's response
        ai_response = result['choices'][0]['message']['content']
        print(f"[Name Verification] AI Response: {ai_response}")
        
        # Parse JSON response
        import json
        import re
        
        # Try multiple extraction methods
        parsed = None
        
        # Method 1: Extract from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Method 2: Extract plain JSON object
        if not parsed:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        
        # Method 3: Try parsing the entire response as JSON
        if not parsed:
            try:
                parsed = json.loads(ai_response.strip())
            except json.JSONDecodeError:
                pass
        
        if parsed and isinstance(parsed, dict):
            return {
                'match': bool(parsed.get('match', False)),
                'confidence': float(parsed.get('confidence', 0.5)),
                'reason': str(parsed.get('reason', 'AI analysis completed'))
            }
        else:
            # Fallback if JSON parsing fails
            print(f"[Name Verification] Failed to parse AI response. Raw response: {ai_response[:200]}")
            return {
                'match': False,
                'confidence': 0.0,
                'reason': f'Could not parse AI response. Raw: {ai_response[:100]}'
            }
            
    except requests.exceptions.RequestException as e:
        print(f"[Name Verification] API Error: {str(e)}")
        # Fallback to simple comparison on API error
        simple_match = customer_name.lower().strip() == salary_slip_name.lower().strip()
        return {
            'match': simple_match,
            'confidence': 1.0 if simple_match else 0.0,
            'reason': f'API error, used fallback comparison: {str(e)}'
        }
    except Exception as e:
        print(f"[Name Verification] Unexpected Error: {str(e)}")
        return {
            'match': False,
            'confidence': 0.0,
            'reason': f'Verification failed: {str(e)}'
        }


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("Rajesh Kumar", "Kumar Rajesh"),
        ("John Smith", "John A. Smith"),
        ("Robert Johnson", "Bob Johnson"),
        ("Mary Williams", "Maria Williams"),
        ("David Lee", "John Smith"),  # Should not match
    ]
    
    print("=" * 60)
    print("Name Verification Tests")
    print("=" * 60)
    
    for customer, salary in test_cases:
        print(f"\nTest: '{customer}' vs '{salary}'")
        result = verify_names_match(customer, salary)
        print(f"Result: {result}")
        print(f"Match: {'✅ YES' if result['match'] else '❌ NO'} (Confidence: {result['confidence']:.2f})")
        print(f"Reason: {result['reason']}")
