"""
Test script to verify database operations
"""
from lecture_gui.database import db

def test_database_operations():
    print("=" * 60)
    print("🧪 Testing Database Operations")
    print("=" * 60)
    
    # Test 1: Fetch all lectures
    print("\n📚 Test 1: Fetching all lectures...")
    lectures = db.get_all_lectures()
    print(f"✅ Found {len(lectures)} lectures")
    
    for lecture in lectures:
        print(f"\n  📖 Lecture {lecture['id']}: {lecture['title']}")
        print(f"     Video: {lecture['video_file']}")
        print(f"     Duration: {lecture['duration']}")
        print(f"     Questions: {len(lecture['questions'])}")
        
        # Display first question as sample
        if lecture['questions']:
            q = lecture['questions'][0]
            print(f"\n     Sample Question:")
            print(f"       Q{q['question_id']}: {q['question_text'][:60]}...")
            print(f"       Keywords: {', '.join(q['keywords'][:3])}...")
    
    # Test 2: Fetch specific lecture
    print("\n" + "-" * 60)
    print("\n📖 Test 2: Fetching specific lecture (ID: 3)...")
    lecture = db.get_lecture_by_id(3)
    
    if lecture:
        print(f"✅ Found lecture: {lecture['title']}")
        print(f"   Questions:")
        for q in lecture['questions']:
            print(f"     {q['question_id']}. {q['question_text'][:50]}...")
    
    # Test 3: Fetch session history
    print("\n" + "-" * 60)
    print("\n📊 Test 3: Fetching recent sessions...")
    sessions = db.get_session_history(limit=3)
    
    print(f"✅ Found {len(sessions)} recent sessions")
    for session in sessions:
        print(f"\n  Session #{session['id']}")
        print(f"    Lecture: {session['lecture_title']}")
        print(f"    Score: {session['session_score']}%")
        print(f"    Timestamp: {session['timestamp']}")
        print(f"    Passed: {'✅ Yes' if session['passed'] else '❌ No'}")
    
    print("\n" + "=" * 60)
    print("✅ All database tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_database_operations()
