"""
Test script to verify installation and configuration.
Run this before using the main application.
"""
import os
import sys

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    errors = []
    
    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        errors.append("openai")
    
    try:
        import langchain
        print("  ✓ langchain")
    except ImportError:
        errors.append("langchain")
    
    try:
        import chromadb
        print("  ✓ chromadb")
    except ImportError:
        errors.append("chromadb")
    
    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        errors.append("requests")
    
    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        errors.append("python-dotenv")
    
    try:
        import PyPDF2
        print("  ✓ PyPDF2")
    except ImportError:
        errors.append("PyPDF2")
    
    if errors:
        print(f"\n❌ Missing packages: {', '.join(errors)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All required packages installed!\n")
    return True


def test_config():
    """Test configuration and API keys."""
    print("Testing configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check OpenAI key (required)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("  ✓ OPENAI_API_KEY configured")
    else:
        print("  ❌ OPENAI_API_KEY not found (REQUIRED)")
        print("     Add to .env: OPENAI_API_KEY=your_key_here")
        return False
    
    # Check optional keys
    optional_keys = {
        "VOLI_API_KEY": "Amadeus flights",
        "OPENWEATHER_API_KEY": "Weather forecasts",
        "MONUMENTS_API_KEY": "Google Places (monuments)",
        "TICKETMASTER_API_KEY": "Events",
        "GITHUB_TOKEN": "GitHub (higher rate limits)"
    }
    
    missing_optional = []
    for key, description in optional_keys.items():
        if os.getenv(key):
            print(f"  ✓ {key} configured ({description})")
        else:
            missing_optional.append(f"{description} ({key})")
    
    if missing_optional:
        print("\n⚠️  Optional keys not configured:")
        for item in missing_optional:
            print(f"     - {item}")
        print("   Some features may not work without these keys.")
    
    print("\n✓ Configuration check complete!\n")
    return True


def test_modules():
    """Test that our modules can be imported."""
    print("Testing project modules...")
    errors = []
    
    try:
        from agents.base_agent import BaseAgent
        print("  ✓ agents.base_agent")
    except Exception as e:
        errors.append(f"agents.base_agent: {e}")
    
    try:
        from agents.query_parser import QueryParser
        print("  ✓ agents.query_parser")
    except Exception as e:
        errors.append(f"agents.query_parser: {e}")
    
    try:
        from agents.data_collector import DataCollector
        print("  ✓ agents.data_collector")
    except Exception as e:
        errors.append(f"agents.data_collector: {e}")
    
    try:
        from agents.rag_manager import RAGManager
        print("  ✓ agents.rag_manager")
    except Exception as e:
        errors.append(f"agents.rag_manager: {e}")
    
    try:
        from agents.plan_generator import PlanGenerator
        print("  ✓ agents.plan_generator")
    except Exception as e:
        errors.append(f"agents.plan_generator: {e}")
    
    try:
        from core.orchestrator import Orchestrator
        print("  ✓ core.orchestrator")
    except Exception as e:
        errors.append(f"core.orchestrator: {e}")
    
    if errors:
        print("\n❌ Module import errors:")
        for error in errors:
            print(f"   {error}")
        return False
    
    print("\n✓ All project modules can be imported!\n")
    return True


def test_data_files():
    """Test that required data files exist."""
    print("Testing data files...")
    
    if os.path.exists("data/airports_iata.json"):
        print("  ✓ data/airports_iata.json found")
    else:
        print("  ❌ data/airports_iata.json not found")
        return False
    
    print("\n✓ Data files check complete!\n")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print(" " * 15 + "TRAVEL AI ASSISTANT v2")
    print(" " * 18 + "Configuration Test")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test configuration
    results.append(("Configuration", test_config()))
    
    # Test modules
    results.append(("Project Modules", test_modules()))
    
    # Test data files
    results.append(("Data Files", test_data_files()))
    
    # Summary
    print("=" * 60)
    print(" " * 22 + "TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60 + "\n")
    
    if all_passed:
        print("🎉 All tests passed! You're ready to use the Travel AI Assistant.")
        print("   Run: python main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running.")
        print("   See QUICKSTART.md for detailed setup instructions.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
