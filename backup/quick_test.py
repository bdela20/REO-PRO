"""
Quick PropInsight API Test
Fast verification that all services are working
"""

import sys
import os
sys.path.append('.')

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def quick_test():
    """Run a quick test of all services"""
    
    print("🚀 PropInsight Quick API Test")
    print("=" * 40)
    
    # Check environment
    print("🔑 Checking Environment...")
    rentcast_key = os.getenv('RENTCAST_API_KEY')
    print(f"   RentCast API Key: {'✅ Set' if rentcast_key else '❌ Missing'}")
    
    if not rentcast_key:
        print("❌ Cannot proceed without RentCast API key!")
        print("💡 Add RENTCAST_API_KEY to your .env file")
        return False
    
    # Import within app context
    try:
        print("\n🔧 Initializing Flask App...")
        from app import create_app, db
        
        app = create_app()
        
        with app.app_context():
            print("   ✅ Flask app initialized")
            print("   ✅ Database connection established")
            
            # Test services
            print("\n🧪 Testing Services...")
            
            from app.services import PropertyService
            property_service = PropertyService()
            status = property_service.test_all_services()
            
            print(f"   RentCast API: {'✅ Working' if status['rentcast_api'] else '❌ Failed'}")
            print(f"   Census API: {'✅ Working' if status['census_api'] else '❌ Failed'}")
            print(f"   Database: {'✅ Connected' if status['database'] else '❌ Failed'}")
            
            if status['all_services_working']:
                print("\n🎉 All services are working!")
                
                # Quick search test
                print("\n🔍 Testing Quick Search...")
                results = property_service.search_properties_comprehensive("Austin, TX", limit=3)
                
                if results['status'] == 'success':
                    print(f"   ✅ Found {results['total_found']} properties")
                    print(f"   ✅ Demographics: {'Included' if results['demographics'] else 'Missing'}")
                    
                    if results['properties']:
                        sample = results['properties'][0]
                        print(f"   📍 Sample: {sample.get('address', 'N/A')}")
                    
                    print("\n🎉 SUCCESS! All systems operational.")
                    return True
                else:
                    print(f"   ❌ Search failed: {results.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"\n❌ Service issues detected: {status['services_summary']}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n✨ Ready to proceed with building the web interface!")
    else:
        print("\n🔧 Please fix the issues above before continuing.")
        print("💡 Check your .env file and API keys.")

