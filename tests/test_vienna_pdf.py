"""Test Vienna PDF search with filtering."""
import requests

# GitHub API
contents_url = "https://api.github.com/repos/u7127755622-tech/Prova-/contents"
response = requests.get(contents_url, timeout=10)

if response.status_code == 200:
    files = response.json()
    
    # Filter for Vienna-related PDFs
    vienna_variations = ["vienna", "wien"]
    vienna_files = []
    
    for f in files:
        name = f.get("name", "")
        size = f.get("size", 0)
        name_lower = name.lower()
        
        # Check if it's a Vienna PDF
        if name.endswith(".pdf") and any(var in name_lower for var in vienna_variations):
            vienna_files.append({
                "name": name,
                "size": size,
                "url": f.get("download_url"),
                "valid": size > 1000
            })
    
    print("="*60)
    print("Vienna-related PDF files:")
    print("="*60)
    
    for f in vienna_files:
        status = "✅ VALID" if f["valid"] else "❌ CORRUPTED/EMPTY"
        print(f"\n{f['name']}")
        print(f"  Size: {f['size']:,} bytes")
        print(f"  Status: {status}")
        print(f"  URL: {f['url']}")
    
    valid_files = [f for f in vienna_files if f["valid"]]
    corrupted_files = [f for f in vienna_files if not f["valid"]]
    
    print("\n" + "="*60)
    print(f"Summary: {len(valid_files)} valid, {len(corrupted_files)} corrupted")
    print("="*60)
    
    if not valid_files:
        print("\n⚠️  No valid Vienna PDFs found!")
        print("The system will fall back to general travel guides.")
    else:
        print(f"\n✅ Found {len(valid_files)} valid Vienna PDF(s)")
        print("These will be used for RAG context.")
