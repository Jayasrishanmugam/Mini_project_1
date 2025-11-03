"""
Complete migration script to move all data from JSON to MySQL
"""
from lecture_gui.database import db, migrate_lectures_from_config, migrate_json_to_mysql

def main():
    print("=" * 60)
    print("🔄 Starting complete migration to MySQL database")
    print("=" * 60)
    
    # Step 1: Migrate lectures and questions
    print("\n📚 Step 1: Migrating lectures and questions...")
    migrate_lectures_from_config()
    
    # Step 2: Migrate session history
    print("\n📊 Step 2: Migrating session history...")
    migrate_json_to_mysql()
    
    # Step 3: Verify migration
    print("\n✅ Verifying migration...")
    lectures = db.get_all_lectures()
    sessions = db.get_session_history(limit=5)
    
    print(f"\n📊 Migration Summary:")
    print(f"  - Total lectures in database: {len(lectures)}")
    print(f"  - Total questions in database: {sum(len(l.get('questions', [])) for l in lectures)}")
    print(f"  - Recent sessions in database: {len(sessions)}")
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("=" * 60)
    
    # Display lecture details
    if lectures:
        print("\n📚 Lectures in database:")
        for lecture in lectures:
            print(f"  {lecture['id']}. {lecture['title']} - {len(lecture.get('questions', []))} questions")

if __name__ == "__main__":
    main()
