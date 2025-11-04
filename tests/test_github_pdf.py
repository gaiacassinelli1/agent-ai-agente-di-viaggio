"""Test GitHub PDF download."""
import requests

url = "https://raw.githubusercontent.com/u7127755622-tech/Prova-/main/VIENNA_WIEN_SmartGuide.pdf"

print(f"Testing URL: {url}\n")

# Try downloading
response = requests.get(url, timeout=10)
print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Length: {response.headers.get('Content-Length')}")
print(f"Actual bytes received: {len(response.content)}")
print(f"\nFirst 100 bytes: {response.content[:100]}")
print(f"\nFirst 100 bytes as text: {response.content[:100].decode('utf-8', errors='ignore')}")

# Check if it's a redirect or HTML
if b'<html>' in response.content[:200].lower() or b'<!doctype' in response.content[:200].lower():
    print("\n⚠️  WARNING: Received HTML instead of PDF!")
    print("This is likely a GitHub redirect or error page.")

# Try alternative URL formats
print("\n" + "="*60)
print("Trying alternative URL formats...")
print("="*60)

# Try GitHub blob URL
blob_url = url.replace('/raw/', '/blob/')
print(f"\n1. Blob URL: {blob_url}")
response2 = requests.get(blob_url, timeout=10, allow_redirects=True)
print(f"   Status: {response2.status_code}, Bytes: {len(response2.content)}")

# Try with GitHub API
api_url = "https://api.github.com/repos/u7127755622-tech/Prova-/contents/VIENNA_WIEN_SmartGuide.pdf"
print(f"\n2. API URL: {api_url}")
response3 = requests.get(api_url, timeout=10, headers={'Accept': 'application/vnd.github.v3.raw'})
print(f"   Status: {response3.status_code}, Bytes: {len(response3.content)}")
if response3.status_code == 200 and len(response3.content) > 1000:
    print("   ✅ This looks like the actual PDF!")
