#!/usr/bin/env python3
"""
BICLLAMA MVP - X(Twitter) Scraping Test
"""
import requests
from bs4 import BeautifulSoup

def test_x_trends():
    """Test if we can access X trending page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Try to access X explore/trending
    url = "https://x.com/explore/tabs/trending"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        
        # Check if we got redirected or blocked
        if "login" in response.url.lower():
            print("❌ Redirected to login - X requires authentication")
            return False
        
        print("✅ Successfully accessed X")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing X(Twitter) Access...")
    test_x_trends()
