"""
Test script for curl command parsing functionality
"""

import sys
from PyQt5.QtWidgets import QApplication
from curl_tool import CurlDialog

def test_curl_parsing():
    """Test curl command parsing"""
    app = QApplication(sys.argv)
    dialog = CurlDialog()
    
    # Test cases
    test_commands = [
        "curl --location 'https://api.dts3.coway.dev/shared/customized/filter-info?userId=20170104' --header 'Cw-Api-Token: b2460796730a41419510'",
        "curl -X POST 'https://httpbin.org/post' -H 'Content-Type: application/json' -d '{\"name\": \"John\", \"age\": 30}'",
        "curl -X GET 'https://api.github.com/users/octocat' -H 'User-Agent: MyApp/1.0'",
        "curl --request DELETE 'https://api.example.com/users/123' --header 'Authorization: Bearer token123'"
    ]
    
    print("Testing curl command parsing:")
    print("=" * 50)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\nTest {i}:")
        print(f"Input: {cmd}")
        
        try:
            parsed = dialog.parse_curl_command(cmd)
            print(f"URL: {parsed['url']}")
            print(f"Method: {parsed['method']}")
            print(f"Headers: {parsed['headers']}")
            print(f"Data: {parsed['data']}")
            print("✅ Parsed successfully")
        except Exception as e:
            print(f"❌ Parse failed: {e}")
    
    print("\n" + "=" * 50)
    print("Curl parsing test completed!")

if __name__ == "__main__":
    test_curl_parsing()