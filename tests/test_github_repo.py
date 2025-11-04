"""Check GitHub repository contents."""
import requests
import json

# Check repository
repo_url = "https://api.github.com/repos/u7127755622-tech/Prova-"
print(f"Checking repository: {repo_url}\n")

response = requests.get(repo_url, timeout=10)
print(f"Repository status: {response.status_code}")

if response.status_code == 200:
    repo_data = response.json()
    print(f"✅ Repository exists!")
    print(f"   Name: {repo_data.get('name')}")
    print(f"   Description: {repo_data.get('description')}")
    print(f"   Default branch: {repo_data.get('default_branch')}")
else:
    print(f"❌ Repository not found or private")
    print(f"Response: {response.text[:200]}")

# List all files in repository
print("\n" + "="*60)
print("Files in repository:")
print("="*60)

contents_url = "https://api.github.com/repos/u7127755622-tech/Prova-/contents"
response2 = requests.get(contents_url, timeout=10)

if response2.status_code == 200:
    files = response2.json()
    print(f"\nFound {len(files)} files:\n")
    for file in files:
        name = file.get('name', 'Unknown')
        size = file.get('size', 0)
        file_type = file.get('type', 'unknown')
        download_url = file.get('download_url', 'N/A')
        
        print(f"📄 {name}")
        print(f"   Type: {file_type}")
        print(f"   Size: {size} bytes")
        print(f"   Download URL: {download_url}")
        
        # If it's the Vienna PDF, try to download it
        if 'VIENNA' in name.upper() and name.endswith('.pdf'):
            print(f"\n   Testing download...")
            test_response = requests.get(download_url, timeout=10)
            print(f"   Status: {test_response.status_code}")
            print(f"   Actual size: {len(test_response.content)} bytes")
            
            if len(test_response.content) > 1000:
                print(f"   ✅ This looks like a real PDF!")
            else:
                print(f"   ❌ File appears to be empty or corrupted")
                print(f"   Content preview: {test_response.content[:50]}")
        print()
else:
    print(f"❌ Could not list files: {response2.status_code}")
    print(f"Response: {response2.text[:200]}")
