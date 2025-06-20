#!/usr/bin/env python3
"""
Complete API Test Suite for PropInsight
Tests all configured APIs and their integration
"""

import subprocess
import sys

def run_test_script(script_name, description):
    """Run a test script and capture results"""
    print(f"\n🚀 Running {description}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Run complete test suite"""
    print("🎯 PropInsight API Test Suite")
    print("=" * 60)
    print("Testing all APIs for PropInsight integration")
    print("This will test RentCast and Census APIs\n")
    
    tests = [
        ("test_rentcast.py", "RentCast API Tests"),
        ("test_census.py", "Census API Tests")
    ]
    
    results = []
    
    for script, description in tests:
        success = run_test_script(script, description)
        results.append((description, success))
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{description:30} {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ PropInsight APIs are ready for development!")
        print("🚀 You can proceed to Day 7: Data Structure Analysis")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("🔧 Review the errors above and fix API configurations")
        print("📚 Check your .env file and API keys")
    print("=" * 60)

if __name__ == "__main__":
    main()