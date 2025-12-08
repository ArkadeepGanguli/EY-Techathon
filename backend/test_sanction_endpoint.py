"""
Quick test to verify sanction letter endpoint
"""
import requests

# Test the sanction letter download endpoint
BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing Sanction Letter Download Endpoint")
print("=" * 60)

# You'll need to replace this with an actual session ID from your app
# To get a session ID: Start the app, complete a loan application until approval
test_session_id = "test_session_123"

print(f"\n1. Testing GET /api/sanction/generate/{test_session_id}")
print("-" * 60)

try:
    response = requests.get(f"{BASE_URL}/api/sanction/generate/{test_session_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Success! PDF received ({len(response.content)} bytes)")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
        
        # Optionally save the PDF
        with open("test_download.pdf", "wb") as f:
            f.write(response.content)
        print("PDF saved as: test_download.pdf")
    elif response.status_code == 404:
        print(f"❌ Session not found: {test_session_id}")
        print(f"   Response: {response.json()}")
    elif response.status_code == 400:
        print(f"❌ Bad request: {response.json().get('detail')}")
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to backend server")
    print("   Make sure the server is running at http://localhost:8000")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
print("\nNOTE: To test with a real session:")
print("1. Start the application with ./start.bat")
print("2. Complete a loan application through approval")
print("3. Check the browser DevTools Network tab for the session ID")
print("4. Update test_session_id in this script")
print("5. Run this script again")
