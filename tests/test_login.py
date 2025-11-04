"""Test script for the login system.

Run this to verify that all components work correctly.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from login import TravelDB, AuthManager, TripManager


def test_database():
    """Test database creation and operations."""
    print("\n" + "=" * 70)
    print(" " * 25 + "🧪 Testing Database")
    print("=" * 70)
    
    # Use in-memory database for testing
    db = TravelDB(":memory:")
    
    # Test table creation
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['users', 'trips', 'plans', 'interactions']
    for table in expected_tables:
        if table in tables:
            print(f"✅ Table '{table}' created successfully")
        else:
            print(f"❌ Table '{table}' NOT found")
    
    db.close()
    return True


def test_authentication():
    """Test user registration and login."""
    print("\n" + "=" * 70)
    print(" " * 25 + "🔐 Testing Authentication")
    print("=" * 70)
    
    db = TravelDB(":memory:")
    auth = AuthManager(db)
    
    # Test registration
    print("\n📝 Testing registration...")
    success = auth.register("testuser", "testpass123", "test@email.com")
    if success:
        print("✅ User registered successfully")
    else:
        print("❌ Registration failed")
        return False
    
    # Test duplicate registration
    print("\n📝 Testing duplicate registration...")
    success = auth.register("testuser", "another123")
    if not success:
        print("✅ Duplicate registration correctly rejected")
    else:
        print("❌ Duplicate registration should have failed")
    
    # Test login with correct credentials
    print("\n🔑 Testing login with correct credentials...")
    user = auth.login("testuser", "testpass123")
    if user and user['username'] == 'testuser':
        print("✅ Login successful")
        print(f"   User ID: {user['id']}")
        print(f"   Email: {user['email']}")
    else:
        print("❌ Login failed")
        return False
    
    # Test login with wrong password
    print("\n🔑 Testing login with wrong password...")
    user = auth.login("testuser", "wrongpass")
    if user is None:
        print("✅ Login correctly rejected")
    else:
        print("❌ Login should have failed")
    
    # Test password change
    print("\n🔐 Testing password change...")
    user_id = auth.login("testuser", "testpass123")['id']
    success = auth.change_password(user_id, "testpass123", "newpass456")
    if success:
        print("✅ Password changed successfully")
        
        # Verify new password works
        user = auth.login("testuser", "newpass456")
        if user:
            print("✅ New password works")
        else:
            print("❌ New password doesn't work")
    else:
        print("❌ Password change failed")
    
    db.close()
    return True


def test_trip_management():
    """Test trip and plan management."""
    print("\n" + "=" * 70)
    print(" " * 25 + "✈️ Testing Trip Management")
    print("=" * 70)
    
    db = TravelDB(":memory:")
    auth = AuthManager(db)
    trip_mgr = TripManager(db)
    
    # Create test user
    auth.register("traveler", "pass123")
    user = auth.login("traveler", "pass123")
    user_id = user['id']
    
    # Test trip creation
    print("\n📝 Creating trip...")
    trip_id = trip_mgr.create_trip(
        user_id=user_id,
        destination="Paris",
        country="France",
        start_date="2025-11-15",
        end_date="2025-11-19",
        departure_city="Rome"
    )
    print(f"✅ Trip created with ID: {trip_id}")
    
    # Test saving plans
    print("\n💾 Saving plans...")
    plan1_id = trip_mgr.save_plan(trip_id, "Plan version 1 content")
    plan2_id = trip_mgr.save_plan(trip_id, "Plan version 2 content (updated)")
    plan3_id = trip_mgr.save_plan(trip_id, "Plan version 3 content (final)")
    print(f"✅ Saved 3 plan versions")
    
    # Test retrieving latest plan
    print("\n📖 Retrieving latest plan...")
    latest = trip_mgr.get_latest_plan(trip_id)
    if latest and latest['version'] == 3:
        print(f"✅ Latest plan is version {latest['version']}")
    else:
        print("❌ Failed to retrieve latest plan")
    
    # Test retrieving all plans
    print("\n📚 Retrieving all plans...")
    all_plans = trip_mgr.get_all_plans(trip_id)
    if len(all_plans) == 3:
        print(f"✅ Retrieved all 3 plan versions")
    else:
        print(f"❌ Expected 3 plans, got {len(all_plans)}")
    
    # Test saving interactions
    print("\n💬 Saving interactions...")
    trip_mgr.save_interaction(trip_id, "Change hotel", "modification", "Hotel changed")
    trip_mgr.save_interaction(trip_id, "What documents?", "information", "You need passport")
    interactions = trip_mgr.get_trip_interactions(trip_id)
    if len(interactions) == 2:
        print(f"✅ Saved and retrieved 2 interactions")
    else:
        print(f"❌ Expected 2 interactions, got {len(interactions)}")
    
    # Test getting user trips
    print("\n📋 Getting user trips...")
    trips = trip_mgr.get_user_trips(user_id)
    if len(trips) == 1:
        print(f"✅ Found 1 trip for user")
    else:
        print(f"❌ Expected 1 trip, got {len(trips)}")
    
    # Test statistics
    print("\n📊 Getting user statistics...")
    stats = trip_mgr.get_user_stats(user_id)
    print(f"   Total trips: {stats['total_trips']}")
    print(f"   Active trips: {stats['active_trips']}")
    if stats['total_trips'] == 1 and stats['active_trips'] == 1:
        print("✅ Statistics are correct")
    else:
        print("❌ Statistics are incorrect")
    
    # Test trip deactivation
    print("\n🔒 Deactivating trip...")
    trip_mgr.deactivate_trip(trip_id)
    active_trip = trip_mgr.get_active_trip(user_id)
    if active_trip is None:
        print("✅ Trip deactivated successfully")
    else:
        print("❌ Trip still active")
    
    db.close()
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "🧪 TRAVEL AI ASSISTANT - LOGIN SYSTEM TESTS")
    print("=" * 70)
    
    tests = [
        ("Database", test_database),
        ("Authentication", test_authentication),
        ("Trip Management", test_trip_management)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 25 + "📊 TEST SUMMARY")
    print("=" * 70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
